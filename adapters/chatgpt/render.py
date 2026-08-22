#!/usr/bin/env python3
"""Adapter ChatGPT (Codex CLI).

Codex no tiene agentes nombrados por archivo como OpenCode; su unidad de
configuracion es un AGENTS.md global (~/.codex/AGENTS.md) + skills
(~/.agents/skills) + subagentes experimentales en config.toml.

Salida:
    adapters/chatgpt/out/AGENTS.md       guia SDLC consolidada (workflow + roles + gates)
    adapters/chatgpt/out/skills/...      copia directa de core/skills (formato compatible)
    adapters/chatgpt/out/config.toml     modelo por defecto desde profiles (si hay binding)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
import yaml
from foundry import CORE, copy_skills, core_agents, load_profiles

OUT = Path(__file__).resolve().parent / "out"


def build_agents_md() -> str:
    matrix = yaml.safe_load((CORE / "workflow" / "matrix.yaml").read_text(encoding="utf-8"))
    gates = matrix["gates"]
    roles = {}
    for name, info in matrix["agents"].items():
        roles.setdefault(info.get("role", "?"), []).append(name)

    lines = [
        "# AGENTS.md — Guía SDLC-IA (generada por agent-foundry)",
        "",
        "REGLA DE IDIOMA OBLIGATORIA: todas las respuestas e interacciones en ESPAÑOL.",
        "",
        "Eres un asistente de desarrollo que opera bajo el ciclo de vida SDD",
        "(Spec-Driven Development) con gates humanos obligatorios. NO te salte fases.",
        "",
        "## Roles del equipo (usa estos nombres al referirte a especializaciones)",
        "",
    ]
    for role, names in roles.items():
        lines.append(f"- **{role}**: {', '.join(sorted(names))}")
    lines += [
        "",
        "## Flujo obligatorio",
        "",
        "1. Requerimientos (`requirements-discovery`) -> brief.",
        "2. Planificación (`planning`) -> Delta Spec + openapi.yaml.",
        "3. Validación IA (`validator-review`) -> verdict ready / revision-needed.",
        f"4. GATE 1 `{gates['G1']['name']}`: requiere la firma exacta "
        f"`{gates['G1']['signature']}` en el shared context. Sin ella, no descomponer ni implementar.",
        "5. Descomposición -> task board `todo`.",
        "6. Ejecución secuencial (`in_progress`), pre-flight: compilar, tests, grafo actualizado.",
        "7. Calidad (`validation-review`): cobertura >=85%, sin drift.",
        f"8. GATE 2 `{gates['G2']['name']}`: requiere `{gates['G2']['signature']}`. Sin ella, nada de merges.",
        "9. Git-Ops exclusivo de git-executor: feature/* -> develop -> qa -> master.",
        "",
        "## Reglas no negociables",
        "",
        "- Aislamiento: prohibido escribir fuera del repositorio activo.",
        "- Placeholder Guard: `<increment-name>` se resuelve dinámicamente o se pregunta.",
        "- Estados: solo los definidos en core/workflow/states.md; manipulación humana",
        "  de bloques IA = corrupted-state (detenerse).",
        "- Self-healing: máximo 3 reintentos antes de marcar `blocked` y escapar al humano.",
        "- Conventional Commits con scope del incremento.",
        "",
        "## Skills",
        "",
        "Las skills instaladas en ~/.agents/skills definen los estándares técnicos por stack.",
        "Consúltalas antes de implementar según el stack detectado.",
        "",
    ]
    return "\n".join(lines)


def build_config_toml(models_cfg: dict) -> str:
    p = models_cfg["providers"]["chatgpt"]
    lines = [
        "# config.toml — generado por agent-foundry (adapter chatgpt)",
        "# Instalar en ~/.codex/config.toml (revisar colisiones con el tuyo).",
        "",
    ]
    if not p.get("active") or not p.get("models"):
        lines += [
            "# SIN BINDINGS: completa providers.chatgpt en agent-foundry/profiles/models.yaml",
            "# y re-ejecuta tooling/build.sh para fijar model por defecto.",
            "# model = \"<modelo-codex>\"",
        ]
    else:
        tier0 = next(iter(p["tier_bindings"].values()), [])
        if tier0:
            lines.append(f'model = "{p["models"][tier0[0]]["id"]}"')
    return "\n".join(lines) + "\n"


def main() -> int:
    profiles = load_profiles()
    agents_out = OUT / "skills"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "AGENTS.md").write_text(build_agents_md(), encoding="utf-8")
    n = copy_skills(agents_out)
    (OUT / "config.toml").write_text(
        build_config_toml(profiles["models"]), encoding="utf-8")
    print(f"[chatgpt] AGENTS.md generado | {n} skills | config.toml")
    print(f"[chatgpt] agentes individuales: N/A (Codex usa AGENTS.md único; "
          f"subagentes config.toml pendiente API estable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
