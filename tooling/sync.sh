#!/usr/bin/env bash
# Instala las salidas generadas por los adapters en las ubicaciones reales.
# USO CONSCIBLE: sobrescribe la configuracion actual de OpenCode.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/adapters/opencode/out"
TARGET="$HOME/.config/opencode"

if [ ! -d "$OUT/agents" ]; then
  echo "ERROR: no existe $OUT. Ejecuta primero tooling/build.sh" >&2
  exit 1
fi

echo "Esto sobrescribirá:"
echo "  $TARGET/agents/*.md   <- $OUT/agents ($(ls "$OUT/agents" | wc -l) archivos)"
echo "  $TARGET/skills/*      <- $OUT/skills ($(ls "$OUT/skills" | wc -l) skills)"
read -rp "¿Continuar? [y/N] " answer
[ "${answer:-n}" = "y" ] || exit 1

mkdir -p "$TARGET"
# Backup previo: permite rollback instantaneo
BACKUP_DIR="$HOME/.local/share/agent-foundry/backups"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
tar -czf "$BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz" -C "$TARGET" agents skills
echo "Backup: $BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz"

rsync -av --delete "$OUT/agents/" "$TARGET/agents/"
rsync -av --delete "$OUT/skills/" "$TARGET/skills/"
echo "SYNC OK"
echo "Rollback si hace falta:"
echo "  tar -xzf $BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz -C $TARGET"
