#!/usr/bin/env bash
# Instala las skills de orientación documental para ChatGPT Desktop/Codex.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/adapters/chatgpt/out/skills"
TARGET="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"

if [ ! -d "$OUT/project-context-navigation" ] || [ ! -d "$OUT/documentation-reconciliation" ]; then
  echo "ERROR: ejecuta tooling/build.sh primero." >&2
  exit 1
fi

mkdir -p "$TARGET"
for skill in project-context-navigation documentation-reconciliation; do
  rm -rf "$TARGET/$skill"
  cp -a "$OUT/$skill" "$TARGET/$skill"
  echo "Instalada: $TARGET/$skill"
done
echo "SYNC CHATGPT OK"
