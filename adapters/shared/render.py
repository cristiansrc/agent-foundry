#!/usr/bin/env python3
"""Renderizador del adapter OpenCode para agent-foundry.

Lee core/agents/** (agnóstico) + profiles/*.yaml (bindings) y produce en
adapters/opencode/out/ la configuración nativa de OpenCode con paridad 1:1:

    out/agents/<nombre>.md   frontmatter final: description, mode, model,
                             temperature, permission (orden idéntico al legacy)
    out/skills/<skill>/...   copia directa de core/skills
    out/plugin/foundry-model-router.ts  plugin generado desde
                             plugins/opencode/model-router/model-router.ts.tmpl
                             + ROUTING embebido (agente -> provider/model)

Reglas de binding:
- modelo  = tier del agente -> primer modelo de tier_bindings del proveedor activo
- temp    = permissions.yaml (fuente única)
- perms   = permissions.yaml (edit/bash/execute); se omiten si no hay ninguno
- vision  = si el agente exige vision, el modelo elegido debe soportarla
"""
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "core"
PROFILES = ROOT / "profiles"
OUT = ROOT / "adapters" / "opencode" / "out"
PLUGIN_TMPL = ROOT / "plugins" / "opencode" / "model-router" / "model-router.ts.tmpl"
INSTALLED_AGENTS = Path.home() / ".config" / "opencode" / "agents"

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
    candidates = provider["tier_bindings"][tier]
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
    p = pcfg["agents"].get(agent, {})
    perm_keys = [k for k in ("edit", "bash", "execute") if k in p]
    return {
        "model": primary_id,
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
    lines.append(f"temperature: {binding['temperature']}")
    if binding["permission"]:
        lines.append("permission:")
        for k, v in binding["permission"].items():
            lines.append(f"  {k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + body


def render_plugin(manifest: list[dict]) -> Path:
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


def parity_report(outdir: Path) -> list[str]:
    diffs = []
    if not INSTALLED_AGENTS.exists():
        return ["(sin instalación previa en ~/.config/opencode/agents; se omite paridad)"]
    for gen in sorted(outdir.glob("*.md")):
        inst = INSTALLED_AGENTS / gen.name
        if not inst.exists():
            diffs.append(f"NUEVO: {gen.name}")
            continue
        if gen.read_text() != inst.read_text():
            diffs.append(f"DIFIERE: {gen.name}")
    for inst in sorted(INSTALLED_AGENTS.glob("*.md")):
        if not (outdir / inst.name).exists():
            diffs.append(f"SIN GENERAR (existe instalado): {inst.name}")
    return diffs


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
        # El harness tiene un principal recomendado, pero deja los especialistas
        # en `all` para que también aparezcan en el selector manual de OpenCode.
        b["mode"] = "primary" if name in set(harness.get("primary", [])) else "all"
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
    plugin_dest = render_plugin(manifest)
    print(f"== Plugin: {plugin_dest.name} con {len(manifest)} rutas ==")

    # Manifest + paridad
    (OUT / "manifest.yaml").write_text(
        yaml.safe_dump({"provider": "opencode-harness", "agents": manifest}, sort_keys=False,
                       allow_unicode=True), encoding="utf-8")
    (OUT / "config.patch.json").write_text(
        '{\n  "default_agent": "master-orchestrator"\n}\n', encoding="utf-8")
    print("== Paridad contra ~/.config/opencode/agents ==")
    diffs = parity_report(agents_out)
    changed = len([d for d in diffs if not d.startswith("(sin")])
    identical = max(0, count - changed)
    for d in diffs:
        print(f"  {d}")
    print(f"\nGenerados: {count} agentes, {n_skills} skills")
    print(f"Iguales a lo instalado: {identical} | Diferencias: {len(diffs)}"
          if diffs and not diffs[0].startswith("(") else f"Generados: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
