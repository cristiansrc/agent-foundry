#!/usr/bin/env python3
"""Adapter Kiro.

Kiro define agentes como archivos .md con frontmatter en ~/.kiro/agents/
(cuerpo = system prompt) y skills en ~/.kiro/skills/<nombre>/SKILL.md.

Salida:
    adapters/kiro/out/agents/<nombre>.md   un archivo por agente core
    adapters/kiro/out/skills/...           copia directa de core/skills

Mapeo:
- tools          <- permissions.yaml (edit/bash -> write/shell)
- resources      <- skill://.kiro/skills/**/SKILL.md (skills bajo demanda)
- model          <- providers.kiro en profiles/models.yaml (si hay binding;
                    si no, se omite y Kiro usa su default)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
import yaml
from foundry import (copy_skills, core_agents, kiro_tools,
                     load_profiles)

OUT = Path(__file__).resolve().parent / "out"


def resolve_kiro_model(agent: str, models_cfg: dict) -> str | None:
    p = models_cfg["providers"]["kiro"]
    if not p.get("active") or not p.get("models"):
        return None
    info = models_cfg["agent_tiers"].get(agent)
    if not info:
        return None
    for slot in p["tier_bindings"].get(info["tier"], []):
        m = p["models"][slot]
        if m.get("status") == "active" and not (
                info.get("requires") == "vision" and not m.get("vision")):
            return m["id"]
    return None


def render_agent(name: str, fm: dict, body: str, profiles: dict) -> str:
    pcfg = profiles["perms"]["agents"].get(name, {})
    tools = kiro_tools(pcfg)
    model = resolve_kiro_model(name, profiles["models"])
    desc = fm.get("description", name)
    lines = [
        "---",
        f"name: {name}",
        f"description: {desc}",
    ]
    if model:
        lines.append(f'model: "{model}"')
    lines.append(f'tools: [{", ".join(chr(34) + t + chr(34) for t in tools)}]')
    lines.append('includeMcpJson: true')
    lines.append("resources:")
    lines.append('  - "skill://.kiro/skills/**/SKILL.md"')
    welcome = f"{name} listo. ¿Qué necesitás?"
    lines.append(f'welcomeMessage: "{welcome}"')
    lines.append("---")
    # El cuerpo core empieza con la regla de idioma; sirve como prompt directo.
    return "\n".join(lines) + "\n\n" + body


def main() -> int:
    profiles = load_profiles()
    agents_out = OUT / "agents"
    agents_out.mkdir(parents=True, exist_ok=True)
    count = 0
    no_model = []
    for name, fm, body in core_agents():
        content = render_agent(name, fm, body, profiles)
        (agents_out / f"{name}.md").write_text(content, encoding="utf-8")
        if "model:" not in content.split("---")[1]:
            no_model.append(name)
        count += 1
    n = copy_skills(OUT / "skills")
    print(f"[kiro] {count} agentes generados | {n} skills")
    if no_model:
        print(f"[kiro] sin binding de modelo (usa default de Kiro): "
              f"{len(no_model)} agentes — completa providers.kiro en profiles/models.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
