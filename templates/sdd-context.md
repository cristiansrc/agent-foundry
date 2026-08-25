# Shared Context SDD — <increment-name>

> Copiar a `docs/specs/.working/<increment-name>-sdd-context.md` al iniciar el
> incremento. UN solo contexto activo por incremento; anteriores quedan
> `superseded`. Estados y firmas: agent-foundry/core/workflow/states.md.
> Placeholder Guard: reemplazar `<increment-name>` antes de guardar.

## Current status
- requirements-discovery

<!-- Enum válido: requirements-discovery | planning | validator-review |
     revision-needed | validated-not-executed | awaiting-human-plan-approval |
     decomposition-completed | in_progress | blocked | validation-review |
     quality-approved | awaiting-human-qa-approval | merged | archived -->

## Canonical artifacts
| Artefacto | Ruta | Rol |
|-----------|------|-----|
| Requirements brief | docs/specs/requirements/<increment-name>-requirements-brief.md | entrada funcional |
| Delta spec | docs/specs/increments/<increment-name>.md | contrato del incremento |
| OpenAPI | docs/api/openapi.yaml | contratos expuestos |
| Task board | docs/specs/tasks/<increment-name>-task-board.md | descomposición |
<!-- Agregar migraciones/config/graphify-out/GRAPH_REPORT.md si aplican.
     Rutas canónicas: distinguir archivo vs directorio; una ruta inexistente bloquea. -->

## Artifact evidence
| Fecha | Agente | Artefacto verificado | Resultado observado | Estado |
|-------|--------|----------------------|---------------------|--------|
| | | | | pass/fail/blocked |

<!-- pass exige haber leído/listado el archivo real EN ESTE ciclo;
     evidencia contradictoria con el archivo actual prohibe pass. -->

## Spec Validator Approval
verdict: pending-review
reviewed_at: <pendiente>
validator_agent: spec-validator
artifact_set_reviewed: <pendiente>
summary: <pendiente>
invalidated_changes_since: none

<!-- Solo `verdict: ready` EXACTO autoriza descomposición/ejecución.
     Cambios post-ready por planner invalidan el ready: registrar razón en
     invalidated_changes_since y volver a validator-review.
     Prohibido duplicar este heading en otra parte del archivo. -->

## Decisions locked
- <!-- decisión durable + fecha + origen (humano/agente) -->

## Validator findings
- <!-- hallazgos abiertos: id, severidad, artefacto, acción requerida -->

## Resolved findings
- <!-- hallazgos cerrados con referencia al finding original -->

## Open questions
- <!-- preguntas al humano; indicar si son bloqueantes -->

## Stale terms guard
- <!-- términos/aliases obsoletos detectados y su término canónico -->

## Next action
- <!-- agente + acción inmediata; un solo item activo -->

## Handoffs (formato compacto, states.md §6)
<!-- Cada handoff ≤15 líneas: tarea | estado_destino | artefactos (≤7 rutas) |
     commit SHA corto | verificación (comando + exit code) | nota ≤80 chars.
     PROHIBIDO incrustar diffs, logs o código: referenciar rutas. -->
- |

<!-- ═══════════ FIRMAS HUMANAS (única edición humana válida) ═══════════
     Descomentar SOLO cuando corresponda, con formato EXACTO (sin aliases):

## Human Plan Approval: approved_by_user

## Human QA Approval: approved_by_user
     Cualquier otra edición humana sobre estados/veredictos = corrupted-state. -->
