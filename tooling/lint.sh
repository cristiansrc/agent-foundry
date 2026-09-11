#!/usr/bin/env bash
# Lint anti-drift de agent-foundry.
# Falla si core/ menciona modelos concretos, rutas absolutas o frontmatter roto.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE="$ROOT/core"
ERRORS=0

fail() { echo "FAIL: $1"; ERRORS=$((ERRORS+1)); }

echo "== Anti-drift: modelos concretos en core/"
if grep -rInE 'opencode/|opencode-go/|mimo-v2\.5|muse-spark|deepseek-v4|minimax-m3|gpt-5\.6-luna|\bhy3\b|qwen3\.[67]' "$CORE"; then
  fail "referencias a modelos dentro de core/"
else
  echo "OK"
fi

echo "== Anti-drift: rutas absolutas /home/"
if grep -rInE '/home/[a-zA-Z_]+' "$CORE"; then
  fail "rutas absolutas en core/"
else
  echo "OK"
fi

echo "== Anti-drift: model:/temperature:/permission: en frontmatter de agentes"
VIOLATIONS=$(awk '/^---$/{c++; next} c==1 && /^(model|temperature|permission):/ {print FILENAME": "$0}' \
  $(find "$CORE/agents" -name '*.md'))
if [ -n "$VIOLATIONS" ]; then
  echo "$VIOLATIONS"
  fail "frontmatter con binding de ejecución"
else
  echo "OK"
fi

echo "== Frontmatter presente y role declarado"
while IFS= read -r f; do
  head -1 "$f" | grep -q '^---$' || fail "sin frontmatter: $f"
  grep -q '^role:' "$f" || fail "sin role: $f"
done < <(find "$CORE/agents" -name '*.md')
echo "OK"

echo "== YAML válido en workflow/ y profiles/"
if command -v python3 >/dev/null && python3 -c 'import yaml' 2>/dev/null; then
  find "$ROOT/workflow" "$CORE/workflow" "$ROOT/profiles" -name '*.yaml' 2>/dev/null | while IFS= read -r f; do
    python3 -c "import yaml,sys; yaml.safe_load(open('$f'))" || echo "YAML inválido: $f"
  done
  echo "OK"
else
  echo "SKIP (pyyaml no disponible)"
fi

echo "== Plugin model-router: template y anti-drift =="
if [ ! -f "$ROOT/plugins/opencode/model-router/model-router.ts.tmpl" ]; then
  fail "falta template plugins/opencode/model-router/model-router.ts.tmpl"
elif ! grep -q '__ROUTING_JSON__' "$ROOT/plugins/opencode/model-router/model-router.ts.tmpl"; then
  fail "template del plugin sin placeholder __ROUTING_JSON__"
else
  echo "OK (template + placeholder)"
fi
if grep -rInE 'opencode-go/[a-z0-9]|openai/gpt|gpt-5\.6-(luna|terra|sol)|deepseek-v4|mimo-v2\.5|minimax-m3|muse-spark|glm-5\.3|longcat|qwen3' \
    "$ROOT/plugins/opencode/model-router/model-router.ts.tmpl" 2>/dev/null; then
  fail "modelo concreto hardcodeado en template del plugin (solo __ROUTING_JSON__)"
else
  echo "OK (template sin modelos)"
fi
if [ -f "$ROOT/adapters/opencode/out/plugin/foundry-model-router.ts" ]; then
  if grep -q '__ROUTING_JSON__' "$ROOT/adapters/opencode/out/plugin/foundry-model-router.ts"; then
    fail "plugin generado con placeholder sin sustituir (corre build.sh)"
  else
    echo "OK (plugin generado sustituido)"
  fi
else
  echo "SKIP (out/plugin aún no generado; corre build.sh)"
fi

echo "== Constraints: independencia verifier/implementer y packs =="
if command -v python3 >/dev/null && python3 -c 'import yaml' 2>/dev/null; then
  if ! python3 "$ROOT/tooling/check_constraints.py"; then
    fail "constraints del workflow violadas"
  fi
else
  echo "SKIP (pyyaml no disponible)"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "LINT OK"
else
  echo "LINT FALLÓ: $ERRORS error(es)"
  exit 1
fi
