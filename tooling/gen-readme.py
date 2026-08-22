#!/usr/bin/env python3
"""Genera las tablas de agentes/skills/modelos del README entre marcadores.

Uso: python3 tooling/gen-readme.py
Mantiene el README sincronizado con core/ y profiles/ (anti-drift documental).
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"
README = ROOT / "README.md"

BEGIN = "<!-- BEGIN:GENERATED-TABLES -->"
END = "<!-- END:GENERATED-TABLES -->"

ROLE_LABEL = {
    "worker": "Worker (obrero)",
    "consultant": "Consultant (consultor)",
    "validator": "Validator (validador)",
    "guardrail": "Guardrail",
    "personal": "Personal",
}

SKILL_CATEGORIES = [
    ("Arquitectura y Metodología", [
        "hexagonal-architecture", "spec-driven-development", "spec-remediation",
        "openapi-first", "requirements-gathering", "api-governance-linter",
        "design-patterns-standard", "enterprise-architecture-standard",
        "refactor-patterns", "refactor-hexagonal-bridge", "repository-dto-patterns",
        "project-context-files"]),
    ("Backend y Lenguajes", [
        "springboot-stack", "java-stack", "kotlin-stack", "golang-stack",
        "python-stack", "fastapi-stack", "nodejs-stack", "jpa-stack",
        "spring-cloud-gateway", "openapi-standard", "restful-standard",
        "springboot-java-rest-error-response-standards",
        "springboot-kotlin-rest-error-response-standards",
        "fastapi-rest-error-response-standards"]),
    ("Datos y Mensajería", [
        "flyway-migrations", "zero-downtime-migrations", "postgresql-standard",
        "mysql-standard", "oracle-standard", "sqlserver-standard",
        "rabbitmq-standard", "kafka-standard", "amazon-sqs-standard"]),
    ("Frontend y Diseño UI/UX", [
        "frontend-architecture", "react-stack", "angular-stack", "minimalist-ui",
        "ui-design-exploration", "design-to-code", "design-systems",
        "ux-heuristics", "accessibility-standard"]),
    ("Seguridad y Calidad", [
        "security-standards", "keycloak-standard", "code-quality-and-sonarqube",
        "testing-strategy", "functional-testing-standard", "performance-testing-k6",
        "root-cause-analysis", "pre-flight-check", "bug-fixing-workflow",
        "code-review-checklist", "docker-standard", "observability-standard"]),
    ("Orquestación y Documentación", [
        "git-ops", "documentation-lifecycle", "documentation-standards",
        "context-curation", "context-pinning", "workspace-coordination",
        "eval-ops-agent-benchmarks", "graphify"]),
    ("Asistentes Personales", [
        "hyprmind-delegation-protocol", "hyprmind-memory-manager",
        "hyprmind-workspace-manager"]),
    ("Sistema Local (ambxst / Linux)", [
        "ambxst-shell-dev", "ambxst-plugins", "ambxst-theming",
        "ambxst-packaging", "linux-dev"]),
]


def parse_fm(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, ""
    end = text.find("\n---", 3)
    fm = {}
    for line in text[4:end].split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:].lstrip("\n")


def clean_desc(desc: str) -> str:
    d = re.sub(r"\(IDIOMA:\s*ESPA[ÑN]OL?\)\s*", "", desc, flags=re.I)
    return d.replace("|", "\\|").replace("\n", " ").strip()


def agents_tables() -> str:
    order = {"worker": 0, "consultant": 1, "validator": 2, "guardrail": 3}
    sdlc, personal = [], []
    for src in sorted(CORE.glob("agents/**/*.md")):
        fm, _ = parse_fm(src)
        role = fm.get("role", "?")
        row = (src.stem, ROLE_LABEL.get(role, role),
               clean_desc(fm.get("description", "")))
        if role == "personal":
            personal.append(row)
        else:
            sdlc.append((order.get(role, 9), *row))

    lines = ["## Agentes", ""]
    lines += [f"### Ciclo de desarrollo de software ({len(sdlc)})", "",
              "| Agente | Rol | Descripción |", "|--------|-----|-------------|"]
    for _, name, role_label, desc in sorted(sdlc):
        lines.append(f"| `{name}` | {role_label} | {desc} |")
    lines += ["", f"### Asistentes personales — HyprMind ({len(personal)})", "",
              "*Fuera del SDLC; interactúan contigo y delegan al flujo de desarrollo.*",
              "", "| Agente | Descripción |", "|--------|-------------|"]
    for name, _, desc in sorted(personal):
        lines.append(f"| `{name}` | {desc} |")
    return "\n".join(lines)


def skills_table() -> str:
    existing = {}
    for p in (CORE / "skills").glob("*/SKILL.md"):
        fm, body = parse_fm(p)
        desc = fm.get("description") or next(
            (l.strip("# ").strip() for l in body.split("\n") if l.startswith("# ")), "")
        existing[p.parent.name] = clean_desc(desc)

    lines = ["## Skills (73)", ""]
    categorized = set()
    for cat, names in SKILL_CATEGORIES:
        present = [n for n in names if n in existing]
        if not present:
            continue
        categorized.update(present)
        lines += [f"### {cat}", "", "| Skill | Descripción |", "|-------|-------------|"]
        for n in sorted(present):
            lines.append(f"| `{n}` | {existing[n]} |")
        lines.append("")
    rest = sorted(set(existing) - categorized)
    if rest:
        lines += ["### Otras", "", "| Skill | Descripción |", "|-------|-------------|"]
        for n in rest:
            lines.append(f"| `{n}` | {existing[n]} |")
    return "\n".join(lines).rstrip() + "\n"


def models_tables() -> str:
    manifest_path = ROOT / "adapters/opencode/out/manifest.yaml"
    oc_models = {}
    if manifest_path.exists():
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        oc_models = {a["agent"]: a["model"] for a in manifest["agents"]}
    else:
        print("AVISO: sin build previo; ejecuta tooling/build.sh para la tabla opencode")

    cfg = yaml.safe_load((ROOT / "profiles" / "models.yaml").read_text(encoding="utf-8"))
    tiers = cfg["agent_tiers"]

    def resolve(provider: str, agent: str) -> str:
        p = cfg["providers"][provider]
        info = tiers.get(agent)
        if not p.get("active") or not info:
            return "—"
        for slot in p["tier_bindings"].get(info["tier"], []):
            m = p["models"][slot]
            if m.get("status") == "active":
                if info.get("requires") == "vision" and not m.get("vision"):
                    continue
                return f"`{m['id']}`"
        return "default del proveedor"

    lines = ["## Modelos por herramienta", ""]
    for provider, label in [("opencode", "OpenCode"),
                            ("chatgpt", "ChatGPT (Codex CLI)"),
                            ("kiro", "Kiro")]:
        active = cfg["providers"][provider].get("active")
        state = "bindings activos" if active else "**sin bindings** (usa default del proveedor)"
        lines += [f"### {label} — {state}", "",
                  "| Agente | Modelo de ejecución |", "|--------|--------------------|"]
        if provider == "opencode":
            rows = [(a, oc_models.get(a, "—")) for a in sorted(oc_models)]
        else:
            rows = [(a, resolve(provider, a)) for a in sorted(tiers)]
        for a, m in rows:
            lines.append(f"| `{a}` | {m} |")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    block = "\n\n".join([agents_tables(), skills_table(), models_tables()])
    new_content = f"{BEGIN}\n\n{block}\n\n{END}"
    if BEGIN in readme:
        updated = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                         lambda _: new_content, readme, flags=re.DOTALL)
    elif END in readme:
        updated = readme.replace(END, new_content.lstrip("\n") + END)
    else:
        updated = readme.rstrip() + f"\n\n{new_content}\n"
    README.write_text(updated, encoding="utf-8")
    n_agents = len(list(CORE.glob("agents/**/*.md")))
    n_skills = len(list((CORE / "skills").glob("*/SKILL.md")))
    print(f"README actualizado: {n_agents} agentes, {n_skills} skills, tablas de modelos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
