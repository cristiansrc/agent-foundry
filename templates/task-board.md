# Task Board — <increment-name>

> Plantilla de `task-decomposer` (skill spec-driven-development §8).
> Destino: docs/specs/tasks/<increment-name>-task-board.md
> Solo se crea/reescribe tras `verdict: ready` + Gate 1 firmado.
> Estados permitidos (superior y tareas): todo | in_progress | done | blocked.
> PROHIBIDOS: decomposition-ready, validator-approved, executing, pending, ready.

- Spec aprobada: <ruta absoluta>
- Shared context usado: <ruta absoluta>
- Estado superior: **todo**
- Pack sugerido: <!-- duo | incremental | completo (matrix.yaml); no altera gates -->

## Tareas

### T1 — <título atómico y verificable>
- Owner esperado: <!-- executor | refactor | database-architect | ... -->
- Dependencias: <!-- T-id o ninguna -->
- Archivos/áreas permitidas: <rutas exactas>
- Pasos de implementación:
  1. 
- Verificación: <!-- comando exacto + criterio de éxito; incluye suite existente -->
- Estado: todo

### T2 — ...
<!-- Reglas:
     - Nada de "implementar backend" genérico: si requiere decisión de
       arquitectura no cerrada, la tarea nace blocked y vuelve a planner/spec-validator.
     - Blocked exige: decisión faltante, artefacto inconsistente o dependencia externa. -->

## Registro de ejecución
| Tarea | Changed files | Verification result | Notas |
|-------|---------------|---------------------|-------|
<!-- Formato handoff compacto (states.md §6): comando + exit code, sin logs crudos. -->
