#!/usr/bin/env bash
# Reconstruye las salidas de todos los adapters activos.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Lint previo =="
"$ROOT/tooling/lint.sh"

echo ""
echo "== Build: opencode =="
python3 "$ROOT/adapters/shared/render.py"

# Fase 5: chatgpt y kiro se agregan aqui cuando sus adapters existan.
echo ""
echo "BUILD OK"
