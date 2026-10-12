#!/usr/bin/env bash
# Instala las salidas generadas por los adapters en las ubicaciones reales.
# USO CONSCIBLE: sobrescribe la configuracion actual de OpenCode.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/adapters/opencode/out"
TARGET="$HOME/.config/opencode"
MODEL_ONLY=0
WORKFLOW_ONLY=0
if [ "${1:-}" = "--models-only" ]; then
  MODEL_ONLY=1
  shift
  [ "$#" -gt 0 ] || { echo "ERROR: --models-only requiere agentes" >&2; exit 1; }
elif [ "${1:-}" = "--workflow-only" ]; then
  WORKFLOW_ONLY=1
  shift
  [ "$#" -eq 0 ] || { echo "ERROR: --workflow-only no acepta argumentos" >&2; exit 1; }
elif [ "$#" -gt 0 ]; then
  echo "ERROR: opción desconocida" >&2
  exit 1
fi

if [ ! -d "$OUT/agents" ]; then
  echo "ERROR: no existe $OUT. Ejecuta primero tooling/build.sh" >&2
  exit 1
fi
if [ ! -f "$OUT/plugin/foundry-model-router.ts" ]; then
  echo "ERROR: falta $OUT/plugin/foundry-model-router.ts. Ejecuta primero tooling/build.sh" >&2
  exit 1
fi

WORKFLOW_SKILLS=(context-pinning documentation-lifecycle enterprise-architecture-standard
  functional-testing-standard planning-context-pack pre-flight-check secret-scanning
  spec-driven-development spec-remediation workspace-coordination)
if [ "$WORKFLOW_ONLY" -eq 1 ]; then
  for generated in "$OUT"/agents/*.md; do
    [ -f "$generated" ] || { echo "ERROR: salida de agentes incompleta" >&2; exit 1; }
  done
  for skill in "${WORKFLOW_SKILLS[@]}"; do
    [ -f "$OUT/skills/$skill/SKILL.md" ] || { echo "ERROR: falta skill generada $skill" >&2; exit 1; }
  done
  [ -d "$TARGET/agents" ] && [ -d "$TARGET/skills" ] || { echo "ERROR: instalación existente requerida para sync acotado" >&2; exit 1; }
  for generated in "$OUT"/agents/*.md; do
    [ -f "$TARGET/agents/$(basename "$generated")" ] || { echo "ERROR: agente instalado inexistente: $(basename "$generated")" >&2; exit 1; }
  done
  echo "Sync workflow acotado: prompts/permisos + ${#WORKFLOW_SKILLS[@]} skills; bindings de modelo/plugin/config/otras skills conservados"
fi

if [ "$MODEL_ONLY" -eq 1 ]; then
  echo "Sync sólo model/routing de: $* (prompts/permisos/skills/config conservados)"
elif [ "$WORKFLOW_ONLY" -eq 0 ]; then
echo "Esto sobrescribirá:"
echo "  $TARGET/agents/*.md   <- $OUT/agents ($(ls "$OUT/agents" | wc -l) archivos)"
echo "  $TARGET/skills/*      <- $OUT/skills ($(ls "$OUT/skills" | wc -l) skills)"
echo "  $TARGET/plugins/foundry-model-router.ts <- $OUT/plugin/foundry-model-router.ts"
echo "  $TARGET/opencode.json <- fusiona default_agent sin tocar MCPs/proveedores"
fi
read -rp "¿Continuar? [y/N] " answer
[ "${answer:-n}" = "y" ] || exit 1

mkdir -p "$TARGET"
# Backup previo: permite rollback instantaneo (plugins solo si existe)
BACKUP_DIR="${AGENT_FOUNDRY_BACKUP_DIR:-$HOME/.local/share/agent-foundry/backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
if [ "$WORKFLOW_ONLY" -eq 1 ]; then
  BACKUP_FILE="$BACKUP_DIR/opencode-workflow-pre-sync-$STAMP.tar.gz"
  BACKUP_ITEMS=(agents)
  for skill in "${WORKFLOW_SKILLS[@]}"; do
    BACKUP_ITEMS+=("skills/$skill")
  done
  tar -czf "$BACKUP_FILE" -C "$TARGET" "${BACKUP_ITEMS[@]}"
  echo "Backup acotado: $BACKUP_FILE"
  python3 "$ROOT/tooling/sync_workflow.py" --generated "$OUT" --installed "$TARGET" --skills "${WORKFLOW_SKILLS[@]}"
  echo "SYNC WORKFLOW OK — bindings de modelo/plugin/config/skills ajenas conservados; reinicia OpenCode"
  exit 0
fi

BACKUP_ITEMS="agents skills"
[ -d "$TARGET/plugins" ] && BACKUP_ITEMS="$BACKUP_ITEMS plugins"
tar -czf "$BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz" -C "$TARGET" $BACKUP_ITEMS
echo "Backup: $BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz"

if [ "$MODEL_ONLY" -eq 1 ]; then
  python3 "$ROOT/tooling/sync_model_bindings.py" --generated "$OUT" --installed "$TARGET" "$@"
  echo "SYNC MODELOS OK — reinicia OpenCode para cargar el cambio"
  exit 0
fi

rsync -av --delete "$OUT/agents/" "$TARGET/agents/"
rsync -av --delete "$OUT/skills/" "$TARGET/skills/"
mkdir -p "$TARGET/plugins"
cp -v "$OUT/plugin/foundry-model-router.ts" "$TARGET/plugins/foundry-model-router.ts"
python3 - "$TARGET/opencode.json" "$OUT/config.patch.json" <<'PY'
import json
import sys
from pathlib import Path

target, patch = map(Path, sys.argv[1:])
current = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
current.update(json.loads(patch.read_text(encoding="utf-8")))
target.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
PY
echo "SYNC OK"
echo "Rollback si hace falta:"
echo "  tar -xzf $BACKUP_DIR/opencode-pre-sync-$STAMP.tar.gz -C $TARGET"
