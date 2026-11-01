#!/usr/bin/env bash
# Instala las skills de orientación documental para ChatGPT Desktop/Codex.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/adapters/chatgpt/out/skills"
TARGET="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"

SKILLS=(project-context-navigation documentation-reconciliation agent-foundry-reader opencode-control agent-foundry-knowledge execution-auditor permission-guardian)
for skill in "${SKILLS[@]}"; do
  if [ ! -f "$OUT/$skill/SKILL.md" ]; then
    echo "ERROR: falta $skill; ejecuta tooling/build.sh primero." >&2
    exit 1
  fi
done

mkdir -p "$TARGET"
for skill in "${SKILLS[@]}"; do
  rm -rf "$TARGET/$skill"
  cp -a "$OUT/$skill" "$TARGET/$skill"
  echo "Instalada: $TARGET/$skill"
done
echo "SYNC CHATGPT OK"
