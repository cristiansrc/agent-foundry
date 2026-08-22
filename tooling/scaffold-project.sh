#!/usr/bin/env bash
# Inicializa un repositorio activo para trabajar con agent-foundry (SDD).
# Uso: bash scaffold-project.sh [ruta-repo]   (default: cwd)
set -euo pipefail
REPO="${1:-.}"
FOUNDRY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

echo "== Scaffold agent-foundry en $(pwd) =="

# 1. Estructura SDD
mkdir -p docs/specs/increments docs/specs/requirements docs/specs/tasks docs/specs/.working docs/designs docs/api

# 2. Master Spec si no existe
if [ ! -f docs/specs/master_spec.md ]; then
  printf '# Master Spec — %s\n\nFuente de verdad funcional consolidada del proyecto.\n' "$(basename "$(pwd)")" > docs/specs/master_spec.md
  echo "  creado: docs/specs/master_spec.md"
fi

# 3. OpenAPI placeholder si no existe
if [ ! -f docs/api/openapi.yaml ]; then
  printf 'openapi: 3.1.0\ninfo:\n  title: %s API\n  version: 0.1.0\npaths: {}\n' "$(basename "$(pwd)")" > docs/api/openapi.yaml
  echo "  creado: docs/api/openapi.yaml"
fi

# 4. MEMORY.md desde plantilla
if [ ! -f MEMORY.md ]; then
  cp "$FOUNDRY/templates/MEMORY.md" MEMORY.md
  echo "  creado: MEMORY.md"
fi

# 5. Pre-push hook (protección de gates)
bash "$FOUNDRY/tooling/hooks/install-pre-push.sh"

# 6. AGENTS.md raíz si no existe (patrón contexto jerárquico)
if [ ! -f AGENTS.md ]; then
  cat > AGENTS.md <<EOF
# AGENTS.md — $(basename "$(pwd)")

## Comandos
- Build: <comando exacto>
- Test: <comando exacto>
- Lint: <comando exacto>

## Estructura
- <carpeta>: <propósito>

## Constraints
- NO editar archivos generados sin revisión.

## Flujo de trabajo (agent-foundry)
- Ciclo SDD: docs/specs/ — estados y gates según agent-foundry/core/workflow/states.md
- Git exclusivo del agente git-executor
- Antes de push a ramas estables: pre-push hook exige firma Gate 2
- Lecciones aprendidas: MEMORY.md (leer antes de diseñar/implementar)
- Grafo de conocimiento: graphify-out/ (reglas en core/workflow/graphify-governance)

## Done cuando
- <criterio verificable>
EOF
  echo "  creado: AGENTS.md"
else
  echo "  AGENTS.md ya existe; añade manualmente la sección 'Flujo de trabajo (agent-foundry)' si falta."
fi

echo ""
echo "Scaffold OK. Siguiente paso recomendado: graphify install --project && graphify update ."
