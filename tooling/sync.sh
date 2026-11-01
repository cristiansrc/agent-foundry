#!/usr/bin/env bash
# Compatibilidad de nombre: la instalación se limita al proyecto explícito.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/tooling/install-project.py" "$@"
