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
7. Carriles ODD (## Lane: trivial|fix): sin Gate 1; trivial exige
   '## Reviewer Approval: approved'; fix exige esa firma Y Gate 2.
"""
import re
import sys
from pathlib import Path

STATES = {
    "requirements-discovery", "planning", "validator-review", "revision-needed",
    "validated-not-executed", "awaiting-human-plan-approval",
    "decomposition-completed", "in_progress", "blocked", "validation-review",
    "quality-approved", "awaiting-human-qa-approval", "merged", "archived",
    "corrupted-state", "diagnosis", "odd-defined", "escalated-to-sdd",
}
LANES = {"trivial", "fix", "feature", "workspace"}
ODD_STATES = {"diagnosis", "odd-defined", "escalated-to-sdd"}
REVIEW_SIG = "## Reviewer Approval: approved"
LANE_RE = re.compile(r"^#+\s*Lane\s*:\s*`?([a-z]+)`?\s*$", re.M | re.I)
GATE1_SIG = "## Human Plan Approval: approved_by_user"
GATE2_SIG = "## Human QA Approval: approved_by_user"
SECTION_RE = re.compile(r"^##[ \t]+([^\n]+)$", re.M)
STATUS_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?(?:state:[ \t]*)?`?([a-z][a-z_-]*)`?[ \t]*$",
    re.M,
)


def sections(text: str) -> dict[str, list[str]]:
    """Extrae bloques exactos; firmas comentadas no son autorizaciones."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    headings = list(SECTION_RE.finditer(text))
    result: dict[str, list[str]] = {}
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        result.setdefault(heading.group(1).strip(), []).append(text[heading.end():end])
    return result


def validate_file(path: Path) -> list[str]:
    errors = []
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    blocks = sections(text)
    current = blocks.get("Current status", [])
    approvals = blocks.get("Spec Validator Approval", [])
    lane_matches = list(LANE_RE.finditer(text))
    if len(current) != 1:
        errors.append(f"{path.name}: exige UN bloque 'Current status'")
    if len(approvals) > 1 or any(
        name.startswith("Spec Validator Approval") and name != "Spec Validator Approval"
        for name in blocks
    ):
        errors.append(f"{path.name}: dictámenes activos ambiguos; mover historia a reportes")
    if len(lane_matches) > 1:
        errors.append(f"{path.name}: exige UN carril activo; mover historia a reportes")
    for title in ("Human Plan Approval", "Human QA Approval"):
        if sum(name.startswith(title) for name in blocks) > 1 or len(
            blocks.get(f"{title}: approved_by_user", [])
        ) > 1:
            errors.append(f"{path.name}: firmas duplicadas de '{title}'")
    if errors:
        return errors
    # El primer dato es el estado, no un match tomado de la narración posterior.
    first = current[0].strip().splitlines()[0] if current[0].strip() else ""
    m = STATUS_RE.fullmatch(first)
    if not m:
        return [f"{path.name}: Current status requiere 'state: <enum>' como primer dato"]
    status = m.group(1)
    if status not in STATES:
        errors.append(f"{path.name}: estado NO canonico '{status}'")
        errors.append(f"  -> posible corrupcion o alias; detener agentes (corrupted-state)")

    has_gate1 = "Human Plan Approval: approved_by_user" in blocks
    has_gate2 = "Human QA Approval: approved_by_user" in blocks
    approval = approvals[0] if approvals else ""
    verdicts = re.findall(r"^verdict:[ \t]*([^\n]+)$", approval, re.M)
    has_ready = len(verdicts) == 1 and verdicts[0].strip() == "ready"
    if has_ready:
        has_ready = bool(re.search(
            r"^invalidated_by_changes_since:[ \t]*none[ \t]*$", approval, re.M
        ))
    has_review = "Reviewer Approval: approved" in blocks

    lane_m = LANE_RE.search(text)
    lane = lane_m.group(1).lower() if lane_m else "feature"
    if lane not in LANES:
        errors.append(f"{path.name}: carril NO canonico '{lane}'")
        return errors
    if lane in ("trivial", "fix"):
        if status == "diagnosis" and lane != "fix":
            errors.append(f"{path.name}: 'diagnosis' solo existe en carril fix")
        if status in ("quality-approved", "awaiting-human-qa-approval", "merged",
                      "archived") and not has_review:
            errors.append(f"{path.name}: carril {lane} sin '{REVIEW_SIG}'")
        if lane == "fix" and status in ("merged", "archived") and not has_gate2:
            errors.append(f"{path.name}: carril fix promocionado sin firma del Gate 2")
        return errors
    if status in ODD_STATES - {"escalated-to-sdd"}:
        errors.append(f"{path.name}: estado ODD '{status}' en carril {lane}")

    if status in ("validated-not-executed", "awaiting-human-plan-approval",
                  "decomposition-completed", "in_progress") and not has_ready:
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
