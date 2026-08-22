#!/usr/bin/env bash
# Instala el pre-push hook de agent-foundry en el repo actual (cwd).
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/pre-push"
if [ ! -d .git ]; then
  echo "ERROR: ejecuta dentro del repositorio activo."; exit 1
fi
cp "$SRC" .git/hooks/pre-push
chmod +x .git/hooks/pre-push
echo "Pre-push hook instalado en $(pwd)/.git/hooks/pre-push"
echo "Protege: develop, qa, master, main (requiere Gate 2 firmado)."
