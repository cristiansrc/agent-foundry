#!/usr/bin/env python3
"""Test de disponibilidad y latencia de modelos desde profiles/models.yaml.

Uso: python3 test-latency.py [--provider opencode] [--tier sdd_validation]
Prueba cada modelo activo del proveedor con un prompt mínimo vía `opencode run`.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

MODELS_YAML = Path(__file__).resolve().parents[1] / "profiles" / "models.yaml"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="opencode")
    parser.add_argument("--tier", default=None,
                        help="probar solo modelos usados por este tier")
    args = parser.parse_args()

    cfg = yaml.safe_load(MODELS_YAML.read_text(encoding="utf-8"))
    provider = cfg["providers"][args.provider]
    models = provider.get("models", {})
    tier_slots = set()
    if args.tier:
        tier_slots = set(provider["tier_bindings"].get(args.tier, []))

    print(f"=== LATENCIA: {args.provider} ===")
    results = []
    for slot, m in models.items():
        if m.get("status") != "active" or (tier_slots and slot not in tier_slots):
            continue
        mid = m["id"]
        print(f"Probando {mid} ...", flush=True)
        start = time.time()
        try:
            proc = subprocess.run(
                ["opencode", "run", "--model", mid, "Responde únicamente con la palabra OK."],
                capture_output=True, text=True, timeout=20)
            latency = time.time() - start
            ok = proc.returncode == 0 and "OK" in proc.stdout.upper()
            status = "ONLINE" if ok else "ERROR"
            detail = f"{latency:.2f}s" if ok else (proc.stderr.strip() or proc.stdout.strip())[:80]
            print(f"  {'🟢' if ok else '🔴'} {status} | {detail}")
            results.append({"model": mid, "status": status,
                            "latency": f"{latency:.2f}s" if ok else None,
                            "error": None if ok else detail})
        except subprocess.TimeoutExpired:
            print("  ⏳ TIMEOUT (>20s)")
            results.append({"model": mid, "status": "TIMEOUT", "latency": None,
                            "error": ">20s"})
        except Exception as e:
            print(f"  🔴 OFFLINE | {e}")
            results.append({"model": mid, "status": "OFFLINE", "latency": None,
                            "error": str(e)})

    online = sum(1 for r in results if r["status"] == "ONLINE")
    print(f"\nResumen: {online}/{len(results)} online")
    return 0 if online == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
