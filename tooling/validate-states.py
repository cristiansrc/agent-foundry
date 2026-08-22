#!/usr/bin/env python3
"""Validador de integridad de estados SDD (Fase 8).

Audita los shared contexts de un repositorio activo contra la maquina de
estados canonica (core/workflow/states.md). Uso:

    python3 validate-states.py [ruta-repo]     # default: cwd

Verifica por cada docs/specs/.working/<increment>-sdd-context.md:
1. El estado actual pertenece al enum canonico.
2. Gate 1: awaiting-human-plan-approval exige veredicto ready del spec-validator.
3. Firma humana con formato EXACTO (sin aliases).
4. Ejecucion (in_progress) exige Gate 1 firmado.
5. quality-approved / Gate 2 exigen validacion previa registrada.
6. Promocion git (merged) exige firma del Gate 2.
"""
import re
import sys
from pathlib import Path

STATES = {
    "requirements-discovery", "planning", "validator-review", "revision-needed",
    "validated-not-executed", "awaiting-human-plan-approval",
    "decomposition-completed", "in_progress", "blocked", "validation-review",
    "quality-approved", "awaiting-human-qa-approval", "merged", "archived",
    "corrupted-state",
}
GATE1_SIG = "## Human Plan Approval: approved_by_user"
GATE2_SIG = "## Human QA Approval: approved_by_user"
STATUS_RE = re.compile(r"^#+\s*Current status\s*:?\s*$\n?\s*[-*]?\s*`?([a-z_-]+)`?",
                       re.M | re.I)
VERDICT_READY = re.compile(r"verdict\s*:\s*ready", re.I)


def validate_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8")
    m = STATUS_RE.search(text)
    if not m:
        return [f"{path.name}: sin bloque 'Current status' legible"]
    status = m.group(1).strip()
    if status not in STATES:
        errors.append(f"{path.name}: estado NO canonico '{status}'")
        errors.append(f"  -> posible corrupcion o alias; detener agentes (corrupted-state)")

    has_gate1 = GATE1_SIG in text
    has_gate2 = GATE2_SIG in text
    has_ready = bool(VERDICT_READY.search(text))

    if status == "awaiting-human-plan-approval" and not has_ready:
        errors.append(f"{path.name}: Gate 1 sin 'Spec Validator Approval verdict: ready' previo")
    if status in ("decomposition-completed", "in_progress") and not has_gate1:
        errors.append(f"{path.name}: ejecucion/descomposicion sin firma del Gate 1")
    if status == "quality-approved" and not has_gate1:
        errors.append(f"{path.name}: quality-approved sin Gate 1 registrado")
    if status == "awaiting-human-qa-approval" and not has_gate1:
        errors.append(f"{path.name}: espera de Gate 2 sin Gate 1 registrado")
    if status in ("merged", "archived") and not has_gate2:
        errors.append(f"{path.name}: promocion/archivo sin firma del Gate 2")

    # Firmas con formato incorrecto (aliases tipicos)
    for bad in re.finditer(r"^#+\s*Human (Plan|QA) Approval\s*:\s*(.+)$", text, re.M):
        sig_line, value = bad.group(0), bad.group(2).strip()
        if sig_line.strip() not in (GATE1_SIG, GATE2_SIG):
            errors.append(f"{path.name}: firma humana MAL FORMADA: '{sig_line.strip()}' "
                          f"(usar exactamente '{GATE1_SIG}' o '{GATE2_SIG}')")
    return errors


def main() -> int:
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    working = repo / "docs" / "specs" / ".working"
    contexts = sorted(working.glob("*-sdd-context.md"))
    if not contexts:
        print(f"Sin shared contexts en {working} (nada que validar)")
        return 0
    total_errors = 0
    for ctx in contexts:
        errs = validate_file(ctx)
        status = "OK" if not errs else f"{len(errs)} ERROR(ES)"
        print(f"[{status}] {ctx.relative_to(repo)}")
        for e in errs:
            print(f"  {e}")
            total_errors += 1
    print(f"\nContexts: {len(contexts)} | Errores: {total_errors}")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
