#!/usr/bin/env python3
"""Gate determinista de restricciones estructurales del workflow.

Valida constraints declaradas en core/workflow/matrix.yaml (seccion
constraints) contra la propia matriz. Cero LLM: joins sobre datos.
Uso: python3 check_constraints.py   (invocado por tooling/lint.sh)
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "core" / "workflow" / "matrix.yaml"

EXECUTION_STATES = {"in_progress"}
PROMOTION_STATES = {"merged", "archived"}
VALID_ROLES_WORKER = {"worker"}
VALID_ROLES_VALIDATOR = {"validator"}


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def main() -> int:
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    agents = matrix.get("agents", {})
    constraints = (matrix.get("constraints") or {}).get("verifier_independence") or {}
    errors: list[str] = []

    for worker, validators in (constraints.get("forbidden_pairs") or {}).items():
        entry = agents.get(worker)
        if entry is None:
            fail(f"forbidden_pairs: worker inexistente en matrix: {worker}", errors)
            continue
        if entry.get("role") not in VALID_ROLES_WORKER:
            fail(f"forbidden_pairs: '{worker}' no es worker (role={entry.get('role')})", errors)
        for validator in validators:
            v = agents.get(validator)
            if v is None:
                fail(f"forbidden_pairs[{worker}]: validador inexistente: {validator}", errors)
                continue
            if v.get("role") not in VALID_ROLES_VALIDATOR:
                fail(
                    f"forbidden_pairs[{worker}]: '{validator}' no es validator "
                    f"(role={v.get('role')})",
                    errors,
                )

    # Invariante: validadores jamas escriben estados de ejecucion/promocion.
    for name, entry in agents.items():
        if entry.get("role") in VALID_ROLES_VALIDATOR:
            writes = set(entry.get("writes_states") or [])
            bad_exec = writes & EXECUTION_STATES
            bad_promo = writes & PROMOTION_STATES
            if bad_exec:
                fail(f"validador '{name}' escribe estados de ejecucion: {sorted(bad_exec)}", errors)
            if bad_promo:
                fail(f"validador '{name}' escribe estados de promocion: {sorted(bad_promo)}", errors)

    # Coherencia de packs: agentes listados existen; activa presente.
    packs = matrix.get("packs") or {}
    if not packs:
        fail("matrix sin seccion packs (perfiles duo/incremental/completo)", errors)
    for pack_name, pack in packs.items():
        activa = pack.get("activa")
        if isinstance(activa, str):
            # descripcion libre (p.ej. ciclo completo); nada que validar por miembro
            activa = []
        elif activa is None:
            activa = []
            fail(f"packs.{pack_name}: sin campo 'activa'", errors)
        soporte = pack.get("soporte_bajo_demanda") or []
        if not isinstance(soporte, list):
            fail(f"packs.{pack_name}: 'soporte_bajo_demanda' debe ser lista", errors)
            soporte = []
        for member in list(activa) + soporte:
            if member not in agents:
                fail(f"packs.{pack_name}: agente inexistente en matrix: {member}", errors)

    if errors:
        print("== Constraints del workflow ==")
        for e in errors:
            print(f"FAIL: {e}")
        print(f"CONSTRAINTS FALLARON: {len(errors)} error(es)")
        return 1
    print("== Constraints del workflow ==")
    print("OK (verifier independence, roles, packs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
