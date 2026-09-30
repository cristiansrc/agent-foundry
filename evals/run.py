#!/usr/bin/env python3
"""Runner de evaluaciones de agentes (EvalOps).

Uso:
    python3 evals/run.py evals/cases/spec-validator.yaml                 # dry-run
    python3 evals/run.py evals/cases/spec-validator.yaml --executor opencode

--executor echo   : no invoca modelo; valida formato de casos (default)
--executor opencode : ejecuta `opencode run` con el agente real y el modelo
                      asignado en su perfil; grep del expect_contains.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def run_case_opencode(agent: str, model: str | None, system: str, user_input: str,
                      timeout: int) -> str:
    """Ejecuta el caso en un sandbox temporal vacío.

    El cwd aislado evita que el agente explore/escriba en agent-foundry y
    fuerza a evaluar solo con el contexto inline del caso.
    """
    with tempfile.TemporaryDirectory(prefix="foundry-eval-") as sandbox:
        cmd = ["opencode", "run", "--dir", sandbox, "--agent", agent]
        if model:
            cmd += ["--model", model]
        cmd.append(f"{system}\n\n---\n\n{user_input}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=timeout, cwd=sandbox)
        except subprocess.TimeoutExpired:
            return f"__TIMEOUT__ ({timeout}s)"
    return result.stdout + result.stderr


def evaluate(out: str, expect: str | None, expect_regex: str | None,
             expect_not: str | None) -> tuple[bool, str]:
    if out.startswith("__TIMEOUT__"):
        return False, out
    if expect_regex:
        ok = re.search(expect_regex, out, flags=re.IGNORECASE) is not None
        detail = f"regex '{expect_regex}' {'encontrado' if ok else 'NO encontrado'}"
    else:
        ok = expect.lower() in out.lower()
        detail = f"esperado '{expect}' {'encontrado' if ok else 'NO encontrado'}"
    if ok and expect_not and re.search(expect_not, out, flags=re.IGNORECASE):
        return False, f"prohibido '{expect_not}' presente"
    return ok, detail


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite")
    parser.add_argument("--executor", choices=["echo", "opencode"], default="echo")
    parser.add_argument("--model", default=None,
                        help="override del modelo (default: perfil activo)")
    parser.add_argument("--repeat", type=int, default=1,
                        help="ejecuciones por caso (los LLM no son deterministas)")
    parser.add_argument("--threshold", type=float, default=None,
                        help="fracción mínima de ejecuciones PASS (default: mayoría)")
    parser.add_argument("--timeout", type=int, default=900,
                        help="segundos por ejecución (default 900)")
    parser.add_argument("--show-output", action="store_true",
                        help="muestra la respuesta del agente para diagnosticar un caso")
    args = parser.parse_args()

    suite = yaml.safe_load(Path(args.suite).read_text(encoding="utf-8"))
    agent = suite["agent"]
    passed = failed = 0

    print(f"Suite: {args.suite} | agente: {agent} | executor: {args.executor}")
    if args.executor == "echo":
        print("(dry-run: solo valida estructura de casos)\n")

    for case in suite["cases"]:
        cid = case["id"]
        expect = case.get("expect_contains")
        expect_regex = case.get("expect_regex")
        if not expect and not expect_regex:
            raise ValueError(f"caso {cid} requiere expect_contains o expect_regex")
        if args.executor == "echo":
            ok = bool(case.get("input", "").strip())
            detail = "formato OK" if ok else "caso mal formado"
            out = ""
        else:
            runs = []
            for _ in range(max(1, args.repeat)):
                out = run_case_opencode(agent, args.model, suite.get("system_context", ""),
                                        case["input"], args.timeout)
                runs.append(evaluate(out, expect, expect_regex, case.get("expect_not_regex")))
            wins = sum(1 for r_ok, _ in runs if r_ok)
            need = args.threshold if args.threshold is not None else 0.5
            ok = wins / len(runs) > need if args.threshold is None else wins / len(runs) >= need
            detail = f"{wins}/{len(runs)} — {runs[-1][1]}"
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {cid}: {case['description']} ({detail})")
        if args.executor == "opencode" and args.show_output and (not ok):
            print("--- salida del agente (diagnóstico) ---")
            print(out[:8000].rstrip())
            if len(out) > 8000:
                print("[salida truncada a 8000 caracteres]")
            print("--- fin salida ---")
        passed, failed = passed + ok, failed + (not ok)

    print(f"\nResultado: {passed} pass / {failed} fail / {passed+failed} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
