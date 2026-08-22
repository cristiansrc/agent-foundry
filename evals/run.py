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
import subprocess
import sys
from pathlib import Path

import yaml


def run_case_opencode(agent: str, model: str | None, system: str, user_input: str) -> str:
    cmd = ["opencode", "run", "--agent", agent]
    if model:
        cmd += ["--model", model]
    cmd.append(f"{system}\n\n---\n\n{user_input}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout + result.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite")
    parser.add_argument("--executor", choices=["echo", "opencode"], default="echo")
    parser.add_argument("--model", default=None,
                        help="override del modelo (default: perfil activo)")
    args = parser.parse_args()

    suite = yaml.safe_load(Path(args.suite).read_text(encoding="utf-8"))
    agent = suite["agent"]
    passed = failed = 0

    print(f"Suite: {args.suite} | agente: {agent} | executor: {args.executor}")
    if args.executor == "echo":
        print("(dry-run: solo valida estructura de casos)\n")

    for case in suite["cases"]:
        cid = case["id"]
        expect = case["expect_contains"]
        if args.executor == "echo":
            ok = bool(case.get("input", "").strip()) and bool(expect.strip())
            detail = "formato OK" if ok else "caso mal formado"
        else:
            out = run_case_opencode(agent, args.model,
                                    suite.get("system_context", ""), case["input"])
            ok = expect.lower() in out.lower()
            detail = f"esperado '{expect}' {'encontrado' if ok else 'NO encontrado'}"
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {cid}: {case['description']} ({detail})")
        passed, failed = passed + ok, failed + (not ok)

    print(f"\nResultado: {passed} pass / {failed} fail / {passed+failed} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
