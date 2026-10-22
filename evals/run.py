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
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tooling"))
import sync_workflow


def stage_candidate(candidate: Path, sandbox: Path, agent: str) -> dict:
    """Evalúa salidas nuevas sin instalar; mismo binding que workflow-only."""
    source = candidate / "agents" / f"{agent}.md"
    installed = Path.home() / ".config/opencode"
    content = sync_workflow.compose_agent(source.read_text(encoding="utf-8"),
                                         (installed / "agents" / source.name).read_text(encoding="utf-8")) \
        if (installed / "agents" / source.name).is_file() else source.read_text(encoding="utf-8")
    target = sandbox / ".opencode"
    (target / "agents").mkdir(parents=True)
    (target / "agents" / source.name).write_text(content, encoding="utf-8")
    shutil.copytree(candidate / "skills", target / "skills")
    graphify = target / "skills/graphify/SKILL.md"
    installed_graphify = installed / "skills/graphify/SKILL.md"
    if graphify.is_file() and installed_graphify.is_file():
        shutil.copytree(installed / "skills/graphify", graphify.parent, dirs_exist_ok=True)
        graphify.write_text(sync_workflow.compose_graphify(
            (candidate / "skills/graphify/SKILL.md").read_text(encoding="utf-8"),
            installed_graphify.read_text(encoding="utf-8")), encoding="utf-8")
    # Markdown agents and skills are discovered natively from .opencode.
    # Generating a parallel config entry here used legacy config keys and
    # prevented OpenCode V2 from resolving the staged agent by ID.
    # Huellas de prompts/skills realmente staged; no provider config ni secretos.
    return {str(path.relative_to(target)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(target.rglob("*.md"))}


def sandbox_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or Path(relative).is_absolute():
        raise ValueError(f"ruta de fixture fuera del sandbox: {relative}")
    return path


def verify_files(root: Path, expected: dict) -> list[str]:
    """Comprueba artefactos reales, no claims del modelo sobre sus escrituras."""
    errors = []
    for relative, checks in expected.items():
        path = sandbox_path(root, relative)
        if not path.is_file():
            errors.append(f"{relative}: archivo ausente")
            continue
        text = path.read_text(encoding="utf-8")
        if "equals" in checks and text != checks["equals"]:
            errors.append(f"{relative}: contenido distinto")
        for value in checks.get("contains", []):
            if value not in text:
                errors.append(f"{relative}: falta contenido esperado")
        for value in checks.get("not_contains", []):
            if value in text:
                errors.append(f"{relative}: contenido prohibido")
    return errors


def run_case_opencode(agent: str, model: str | None, system: str, user_input: str,
                      timeout: int, candidate: Path | None = None,
                      evidence: dict | None = None, files: dict | None = None,
                      expected_files: dict | None = None) -> str:
    """Ejecuta el caso en un sandbox temporal vacío.

    El cwd aislado evita que el agente explore/escriba en agent-foundry y
    fuerza a evaluar solo con el contexto inline del caso.
    """
    with tempfile.TemporaryDirectory(prefix="foundry-eval-", dir="/tmp/opencode") as sandbox:
        root = Path(sandbox)
        for relative, content in (files or {}).items():
            path = sandbox_path(root, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        if candidate:
            hashes = stage_candidate(candidate, Path(sandbox), agent)
            if evidence is not None:
                evidence["candidate_sha256"] = hashes
        cmd = ["opencode", "run", "--agent", agent, "--format", "json"]
        if model:
            cmd += ["--model", model]
        cmd.append(f"{system}\n\n---\n\n{user_input}")
        try:
            env = os.environ.copy()
            if candidate:
                # El router global puede sustituir --model por el binding activo,
                # invalidando las evals de candidatos. Aislar el modelo bajo prueba.
                env["OPENCODE_PURE"] = "1"
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=timeout, cwd=sandbox, env=env)
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or "", exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            # Conservar texto parcial emitido sin certificarlo ni evaluar tool logs.
            return f"__TIMEOUT__ ({timeout}s)\n{response_text(stdout)}\n{stderr}"
        if expected_files and result.returncode == 0:
            errors = verify_files(root, expected_files)
            if evidence is not None:
                evidence["file_checks"] = {"pass": not errors, "errors": errors}
            if errors:
                return "__ARTIFACT_ERROR__\n" + "\n".join(errors) + "\n" + response_text(result.stdout)
    if result.returncode:
        return (f"__EXECUTION_ERROR__ ({result.returncode})\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return response_text(result.stdout)


def response_text(events: str) -> str:
    """No evaluar logs, tool output o prompt reflejado como respuesta del modelo."""
    parts = []
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "text":
            part = event.get("part", {})
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
    return "\n".join(parts) if parts else "__NO_RESPONSE__"


def evaluate(out: str, expect: str | None, expect_regex: str | None,
             expect_not: str | None) -> tuple[bool, str]:
    if out.startswith(("__TIMEOUT__", "__EXECUTION_ERROR__", "__NO_RESPONSE__", "__ARTIFACT_ERROR__")):
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
    parser.add_argument("--case", dest="case_id", help="ejecutar sólo un caso identificado")
    parser.add_argument("--stop-on-error", action="store_true", help="no consumir llamadas después del primer fallo")
    parser.add_argument("--candidate-dir", type=Path, help="salidas OpenCode nuevas a evaluar sin sync")
    parser.add_argument("--report", type=Path, help="persistir evidencia JSON por caso (incluye respuesta)")
    args = parser.parse_args()

    suite = yaml.safe_load(Path(args.suite).read_text(encoding="utf-8"))
    agent = suite["agent"]
    passed = failed = 0
    report = {"suite": args.suite, "agent": agent, "executor": args.executor,
              "candidate_dir": str(args.candidate_dir) if args.candidate_dir else None,
              "results": []}

    print(f"Suite: {args.suite} | agente: {agent} | executor: {args.executor}")
    if args.executor == "echo":
        print("(dry-run: solo valida estructura de casos)\n")

    cases = [case for case in suite["cases"] if not args.case_id or case["id"] == args.case_id]
    if not cases:
        parser.error("caso no encontrado")
    for case in cases:
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
            responses = []
            evidence = {}
            for _ in range(max(1, args.repeat)):
                out = run_case_opencode(agent, args.model, suite.get("system_context", ""),
                                        case["input"], args.timeout, args.candidate_dir, evidence,
                                        case.get("files"), case.get("expected_files"))
                responses.append(out)
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
        report["results"].append({"id": cid, "pass": ok, "detail": detail,
                                  "responses": responses if args.executor == "opencode" else []})
        if args.executor == "opencode":
            report["results"][-1].update(evidence)
        if args.report:
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not ok and args.stop_on_error:
            break

    print(f"\nResultado: {passed} pass / {failed} fail / {passed+failed} total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
