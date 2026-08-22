#!/usr/bin/env bash
# Reconstruye las salidas de todos los adapters activos.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Lint previo =="
"$ROOT/tooling/lint.sh"

echo ""
echo "== Build: opencode =="
python3 "$ROOT/adapters/shared/render.py"

echo ""
echo "== Build: chatgpt (Codex) =="
python3 "$ROOT/adapters/chatgpt/render.py"

echo ""
echo "== Build: kiro =="
python3 "$ROOT/adapters/kiro/render.py"

echo ""
echo "BUILD OK"
