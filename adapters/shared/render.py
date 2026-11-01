#!/usr/bin/env python3
"""Renderizador del adapter OpenCode para agent-foundry.

Lee core/agents/** (agnóstico) + profiles/*.yaml (bindings) y produce en
adapters/opencode/out/ la configuración nativa de OpenCode:

    out/agents/<nombre>.md   frontmatter final: description, mode, model,
                             temperature, permission (orden idéntico al legacy)
    out/skills/<skill>/...   copia directa de core/skills
    out/plugin/foundry-model-router.ts  plugin generado desde
                             plugins/opencode/model-router/model-router.ts.tmpl
                             + ROUTING embebido (agente -> provider/model)

Reglas de binding:
- modelo  = tier del agente -> primer modelo de tier_bindings del proveedor activo
              + `variant` opcional de agent_tiers (campo `variant:` del frontmatter)
              + `slot` opcional de agent_tiers (override de modelo dentro del proveedor)
- temp    = permissions.yaml (fuente única)
- perms   = permissions.yaml (edit/bash/execute/task) como mapa `permission:`
            (único formato válido en frontmatter .md; ver render_agent)
- vision  = si el agente exige vision, el modelo elegido debe soportarla
"""
import json
import shutil
import sys
from pathlib import Path

import yaml
from foundry import governed_body

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core"
PROFILES = ROOT / "profiles"
OUT = ROOT / "adapters" / "opencode" / "out"
PLUGIN_TMPL = ROOT / "plugins" / "opencode" / "model-router" / "model-router.ts.tmpl"

DEFAULT_PROVIDER = "opencode"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[4:end].split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    body = text[end + 4:].lstrip("\n")
    return fm, body


def load_profiles() -> dict:
    models = yaml.safe_load((PROFILES / "models.yaml").read_text(encoding="utf-8"))
    perms = yaml.safe_load((PROFILES / "permissions.yaml").read_text(encoding="utf-8"))
    return {"models": models, "perms": perms}


def resolve_binding(agent: str, profiles: dict) -> dict:
    mcfg, pcfg = profiles["models"], profiles["perms"]
    info = mcfg["agent_tiers"].get(agent)
    if not info:
        sys.exit(f"FAIL: agente {agent} sin tier en models.yaml")
    provider_name = info.get("harness_provider", DEFAULT_PROVIDER)
    provider = mcfg["providers"].get(provider_name)
    if provider is None:
        sys.exit(f"FAIL: proveedor harness inexistente para {agent}: {provider_name}")
    if not provider.get("active"):
        sys.exit(f"FAIL: proveedor {provider_name} inactivo en models.yaml")
    tier = info["tier"]
    candidates = list(provider["tier_bindings"][tier])
    # `slot` opcional: override por agente dentro del proveedor (el tier
    # sigue como respaldo si el slot no está activo o no cumple visión).
    slot_override = info.get("slot")
    if slot_override:
        if slot_override not in provider["models"]:
            sys.exit(f"FAIL: slot {slot_override} inexistente en {provider_name} para {agent}")
        candidates = [slot_override] + [s for s in candidates if s != slot_override]
    primary_id = None
    for slot in candidates:
        model = provider["models"][slot]
        if model.get("status") != "active":
            continue
        if info.get("requires") == "vision" and not model.get("vision"):
            continue
        primary_id = model["id"]
        break
    if primary_id is None:
        sys.exit(f"FAIL: sin modelo activo para {agent} (tier {tier})")
    # `variant` va como campo propio del frontmatter: el sufijo `modelo#variant`
    # no es un ID válido (Copilot responde UnknownError; el plugin lo
    # propagaba como modelID). Verificado con OpenCode 1.18.31 el 2026-09-30.
    variant = info.get("variant")
    p = {**pcfg.get("defaults", {}), **pcfg["agents"].get(agent, {})}
    perm_keys = [k for k in ("edit", "bash", "execute", "task", "external_directory", "webfetch", "websearch") if k in p]
    return {
        "model": primary_id,
        "variant": variant,
        "temperature": p.get("temp"),
        "permission": {k: p[k] for k in perm_keys},
        "mode": p.get("mode"),
        "tier": tier,
        "provider": provider_name,
    }


def render_agent(src: Path, binding: dict) -> str:
    fm, body = parse_frontmatter(src.read_text(encoding="utf-8"))
    lines = ["---"]
    desc = fm.get("description", "")
    lines.append(f"description: {desc}")
    lines.append(f"mode: {binding['mode'] or fm.get('mode', 'all')}")
    lines.append(f"model: {binding['model']}")
    if binding.get("variant"):
        lines.append(f"variant: {binding['variant']}")
    lines.append(f"temperature: {binding['temperature']}")
    # Frontmatter de agentes .md: el campo válido es `permission` (mapa).
    # `permissions:` (lista V2) solo existe en config JSON; en .md es campo
    # desconocido -> se enruta a `options` del modelo: NO aplica denies y los
    # proveedores estrictos (GLM) rechazan la petición. Verificado
    # empíricamente con OpenCode 1.18.31 el 2026-09-30.
    if binding["permission"]:
        lines.append("permission:")
        for k, v in binding["permission"].items():
            dumped = yaml.safe_dump({k: v}, allow_unicode=True, sort_keys=False).rstrip()
            lines.extend(f"  {line}" for line in dumped.splitlines())
    lines.append("---")
    return "\n".join(lines) + "\n\n" + governed_body(src, body)


def render_plugin(manifest: list[dict], profiles: dict) -> Path:
    """Genera out/plugin/foundry-model-router.ts desde el tmpl + ROUTING.

    El Task tool de OpenCode no acepta `model` en sus args, así que el
    plugin fuerza el routing en el hook `chat.message` (corre en cada
    sesión, incluidas las hijas creadas por Task).
    """
    if not PLUGIN_TMPL.exists():
        sys.exit(f"FAIL: falta template del plugin: {PLUGIN_TMPL}")
    tmpl = PLUGIN_TMPL.read_text(encoding="utf-8")
    if "__ROUTING_JSON__" not in tmpl:
        sys.exit("FAIL: template del plugin sin placeholder __ROUTING_JSON__")
    routing = {entry["agent"]: entry["model"] for entry in manifest}
    content = tmpl.replace("__ROUTING_JSON__", json.dumps(routing, indent=2, sort_keys=True))
    plugin_out = OUT / "plugin"
    plugin_out.mkdir(parents=True, exist_ok=True)
    dest = plugin_out / "foundry-model-router.ts"
    dest.write_text(content, encoding="utf-8")
    if "__ROUTING_JSON__" in content:
        sys.exit("FAIL: placeholder sin sustituir en plugin generado")
    return dest


def render_guardian(manifest: list[dict]) -> Path:
    template = ROOT / "plugins/opencode/permission-guardian/permission-guardian.ts.tmpl"
    content = template.read_text(encoding="utf-8")
    marker = "__ALLOWED_AGENTS_JSON__"
    if content.count(marker) != 1:
        sys.exit("FAIL: placeholder del Permission Guardian ausente/ambiguo")
    content = content.replace(marker, json.dumps(sorted(entry["agent"] for entry in manifest)))
    dest = OUT / "plugin/foundry-permission-guardian.ts"
    dest.write_text(content, encoding="utf-8")
    return dest


def main() -> int:
    profiles = load_profiles()
    if OUT.exists():
        shutil.rmtree(OUT)
    agents_out = OUT / "agents"
    skills_out = OUT / "skills"
    agents_out.mkdir(parents=True)

    print("== Adapter OpenCode harness: agentes ==")
    count = 0
    manifest = []
    harness = profiles["perms"].get("harness", {})
    deployed = (set(harness.get("primary", [])) |
                set(harness.get("active_subagents", [])) |
                set(harness.get("optional_subagents", [])))
    excluded = set(harness.get("excluded", []))
    unknown = deployed & excluded
    if unknown:
        sys.exit(f"FAIL: agentes en deployed y excluded: {sorted(unknown)}")
    for src in sorted(CORE.glob("agents/**/*.md")):
        name = src.stem
        if name not in deployed:
            continue
        b = resolve_binding(name, profiles)
        # Un único principal visible; especialistas sólo por delegación.
        b["mode"] = "primary" if name in set(harness.get("primary", [])) else "subagent"
        content = render_agent(src, b)
        (agents_out / f"{name}.md").write_text(content, encoding="utf-8")
        manifest.append({"agent": name, "tier": b["tier"], "provider": b["provider"], "model": b["model"]})
        print(f"  {name:28s} [{b['provider']}/{b['tier']}] -> {b['model']}")
        count += 1

    print(f"== Skills: copiando {CORE / 'skills'} ==")
    shutil.copytree(CORE / "skills", skills_out)
    n_skills = len(list(skills_out.glob("*/SKILL.md")))
    print(f"  {n_skills} skills")

    # Plugin model-router (ROUTING embebido desde el manifest)
    plugin_dest = render_plugin(manifest, profiles)
    print(f"== Plugin: {plugin_dest.name} con {len(manifest)} rutas ==")
    render_guardian(manifest)

    # Manifest del bundle generado.
    (OUT / "manifest.yaml").write_text(
        yaml.safe_dump({"provider": "opencode-harness", "agents": manifest}, sort_keys=False,
                       allow_unicode=True), encoding="utf-8")
    (OUT / "config.patch.json").write_text(
        '{\n  "default_agent": "master-orchestrator"\n}\n', encoding="utf-8")
    print(f"\nGenerados: {count} agentes, {n_skills} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
