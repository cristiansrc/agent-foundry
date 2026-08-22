#!/usr/bin/env python3
"""Auditoría de coordinación agente-fase-skill (Fase 7).

Cruza core/workflow/matrix.yaml contra los prompts reales de core/agents/:
1. Skills referenciadas en el cuerpo del agente pero ausentes en matrix.skills
2. Skills declaradas en matrix que el cuerpo nunca menciona
3. Estados mencionados en el cuerpo no declarados en reads/writes_states
4. Referencias rotas: skill nombrada por un agente que no existe en core/skills/
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "core"

STATE_TOKENS = [
    "requirements-discovery", "planning", "validator-review", "revision-needed",
    "validated-not-executed", "awaiting-human-plan-approval", "decomposition-completed",
    "in_progress", "blocked", "validation-review", "quality-approved",
    "awaiting-human-qa-approval", "merged", "archived", "corrupted-state",
    "ready", "todo", "done",
]

# Tokens que NO son skills aunque aparezcan entre backticks
NON_SKILL = set(STATE_TOKENS) | {
    # aliases prohibidos citados como ejemplo
    "validator-approved", "ready-for-decomposition", "decomposition-ready",
    "executing", "pending",
    # resultados de spec-remediator
    "fixed-and-awaiting-validation", "superseded-finding", "blocked-planner-decision",
    "blocked-user-decision", "blocked-validator-process-bug", "blocked-retry-limit",
    # conceptos
    "increment-name", "active-repo", "technical-debt", "feat", "fix", "docs",
    "refactor", "chore", "reviewed_at", "verdict",
}

SKILL_REF = re.compile(r"`([a-z0-9-]+)`")


def main() -> int:
    matrix = yaml.safe_load((CORE / "workflow" / "matrix.yaml").read_text(encoding="utf-8"))
    existing_skills = {p.parent.name for p in (CORE / "skills").glob("*/SKILL.md")}
    agent_names = {p.stem for p in CORE.glob("agents/**/*.md")}
    non_skill = NON_SKILL | agent_names

    issues = 0
    print("=" * 72)
    print("AUDITORIA AGENTE x FASE x SKILL")
    print("=" * 72)
    for src in sorted(CORE.glob("agents/**/*.md")):
        name = src.stem
        body = src.read_text(encoding="utf-8")
        entry = matrix["agents"].get(name)
        if entry is None:
            print(f"\n[{name}] SIN ENTRADA EN MATRIX")
            issues += 1
            continue

        # Skills mencionadas en el cuerpo (backticks, excluye agentes/estados/resultados)
        mentioned = {
            m for m in SKILL_REF.findall(body)
            if m in existing_skills or len(m) > 6 and "-" in m
        } - non_skill
        declared = set(entry.get("skills", []))

        missing_in_matrix = {m for m in mentioned if m in existing_skills} - declared
        stale_in_matrix = declared - mentioned
        broken_refs = set()  # con filtro non_skill ya no hay falsos positivos

        # Estados en cuerpo vs declarados
        body_states = {s for s in STATE_TOKENS if s in body}
        declared_states = set(entry.get("reads_states", [])) | set(entry.get("writes_states", []))
        undeclared_states = body_states - declared_states - {
            # estados universales que todo agente puede ver en flujo general
            "planning", "blocked", "todo", "done", "in_progress", "ready",
        }

        row = []
        if missing_in_matrix:
            row.append(f"skills sin declarar: {sorted(missing_in_matrix)}")
        if stale_in_matrix:
            row.append(f"skills posiblemente obsoletas en matrix: {sorted(stale_in_matrix)}")
        if broken_refs:
            row.append(f"REFERENCIAS ROTAS (skill inexistente): {sorted(broken_refs)}")
        if undeclared_states:
            row.append(f"estados en cuerpo sin declarar: {sorted(undeclared_states)}")

        if row:
            issues += len(row)
            print(f"\n[{name}] ({entry.get('role')}) fases={entry.get('phases')}")
            for r in row:
                print(f"  - {r}")

    # Cobertura inversa: skills que NINGUN agente referencia
    all_referenced = set()
    for src in CORE.glob("agents/**/*.md"):
        all_referenced |= {m for m in SKILL_REF.findall(src.read_text(encoding="utf-8"))}
    orphan_skills = sorted(existing_skills - all_referenced)
    print("\n" + "=" * 72)
    print(f"Skills huerfanas (ningun agente las referencia): {len(orphan_skills)}")
    for s in orphan_skills:
        print(f"  - {s}")

    print(f"\nTotal hallazgos: {issues}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
