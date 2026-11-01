#!/usr/bin/env bash
# Estado del bundle generado respecto al proyecto indicado.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/tooling/install-project.py" "$@"
