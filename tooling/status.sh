#!/usr/bin/env bash
# Muestra el estado de sincronizacion entre lo generado y lo instalado.
# Uso: tooling/status.sh [opencode]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$HOME/.config/opencode"
OUT="$ROOT/adapters/opencode/out"

if [ ! -d "$OUT/agents" ]; then
  echo "Sin build previo. Ejecuta tooling/build.sh"; exit 1
fi

echo "== Agentes: instalado vs generado =="
DRIFT=0
for gen in "$OUT"/agents/*.md; do
  name=$(basename "$gen")
  inst="$TARGET/agents/$name"
  if [ ! -f "$inst" ]; then
    echo "  NO INSTALADO:      $name"; DRIFT=$((DRIFT+1))
  elif ! diff -q "$inst" "$gen" >/dev/null; then
    echo "  DESINCRONIZADO:    $name"; DRIFT=$((DRIFT+1))
  fi
done
for inst in "$TARGET"/agents/*.md; do
  name=$(basename "$inst")
  [ -f "$OUT/agents/$name" ] || { echo "  HUÉRFANO (no viene de core): $name"; DRIFT=$((DRIFT+1)); }
done

echo "== Plugin model-router: instalado vs generado =="
if [ ! -f "$OUT/plugin/foundry-model-router.ts" ]; then
  echo "  SIN GENERAR: corre tooling/build.sh"; DRIFT=$((DRIFT+1))
elif [ ! -f "$TARGET/plugins/foundry-model-router.ts" ]; then
  echo "  NO INSTALADO:      foundry-model-router.ts"; DRIFT=$((DRIFT+1))
elif ! diff -q "$TARGET/plugins/foundry-model-router.ts" "$OUT/plugin/foundry-model-router.ts" >/dev/null; then
  echo "  DESINCRONIZADO:    foundry-model-router.ts"; DRIFT=$((DRIFT+1))
else
  echo "  OK: foundry-model-router.ts"
fi

echo "== Skills: instalado vs generado =="
for gen_dir in "$OUT"/skills/*/; do
  name=$(basename "$gen_dir")
  if ! diff -rq "$gen_dir" "$TARGET/skills/$name" >/dev/null 2>&1; then
    echo "  DESINCRONIZADA:    $name"; DRIFT=$((DRIFT+1))
  fi
done
for inst_dir in "$TARGET"/skills/*/; do
  name=$(basename "$inst_dir")
  [ -d "$OUT/skills/$name" ] || { echo "  HUÉRFANA:          $name"; DRIFT=$((DRIFT+1)); }
done

if [ "$DRIFT" -eq 0 ]; then
  echo "INSTALACIÓN SINCRONIZADA ✓"
else
  echo ""
  echo "Diferencias: $DRIFT. Ejecuta tooling/build.sh && tooling/sync.sh"
  echo "(si editaste ~/.config a mano, ese cambio se perderá al sincronizar)"
fi
exit $([ "$DRIFT" -eq 0 ]; echo $?)
