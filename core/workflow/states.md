# Máquina de Estados del SDLC-IA

Fuente de verdad única para los estados del ciclo de vida. Los agentes NO
declaran estados propios: leen y escriben los definidos aquí. Cualquier estado
fuera de este enum es inválido y activa `corrupted-state`.

## 1. Estados del Incremento (Shared Context)

```
requirements-discovery
      │  (requirements brief)
      ▼
   planning
      │  (delta spec + openapi.yaml)
      ▼
validator-review ──────────────► revision-needed ──┐
      │ (verdict: ready)            ▲               │
      │                             └───────────────┘
      │                             (spec-remediator corrige y revalida)
      ▼
validated-not-executed
      ▼
awaiting-human-plan-approval          ◄═══ GATE HUMANO 1
      │ (## Human Plan Approval: approved_by_user)
      ▼
decomposition-completed
      │ (task board: todo)
      ▼
in_progress          ◄── task board: todo → in_progress → done | blocked
      │ (código + tests + pre-flight ok)
      ▼
validation-review    ◄── reviewer / security-reviewer / final-validation
      │ (cobertura ≥85%, sin drift, sin hallazgos abiertos)
      ▼
quality-approved
      ▼
awaiting-human-qa-approval           ◄═══ GATE HUMANO 2
      │ (## Human QA Approval: approved_by_user)
      ▼
merged                               ◄── git-executor: feature → develop → qa → master
      │ (tag de versión)
      ▼
archived                             ◄── shared context pasa a histórico
```

## 2. Enum Canónico

| Estado | Dueño | Significado |
|--------|-------|-------------|
| `requirements-discovery` | IA | Levantamiento con requirements-analyst |
| `planning` | IA | planner diseña delta spec y contratos |
| `validator-review` | IA | validadores auditando la spec |
| `revision-needed` | IA | veredicto no-ready; requiere remediación |
| `validated-not-executed` | IA | verdict ready; aún sin gate humano |
| `awaiting-human-plan-approval` | GATE | bloqueado hasta firma humana |
| `decomposition-completed` | IA | task board generado en `todo` |
| `in_progress` | IA | implementación activa |
| `blocked` | IA | tarea detenida; exige `blocked_reason`, `conflicting_artifacts`, `required_owner`, `next_required_decision` |
| `validation-review` | IA | auditoría de calidad en curso |
| `quality-approved` | IA | cobertura y calidad certificadas |
| `awaiting-human-qa-approval` | GATE | bloqueado hasta firma humana |
| `merged` | IA | integrado por git-executor tras el gate |
| `archived` | IA | histórico |
| `corrupted-state` | ERROR | manipulación ilegal de bloques de estado |

### Veredictos de Validación (spec-validator)

- `ready`
- `revision-needed`

### Resultados de Remedación (spec-remediator)

- `fixed-and-awaiting-validation`
- `superseded-finding`
- `blocked-planner-decision`
- `blocked-user-decision`
- `blocked-validator-process-bug`
- `blocked-retry-limit`

## 3. Firmas Humanas Válidas (únicas escrituras humanas permitidas)

```
## Human Plan Approval: approved_by_user
## Human QA Approval: approved_by_user
```

Cualquier otra edición humana sobre bloques `## Current status`,
veredictos o auditorías = `corrupted-state`. Los agentes se detienen con
`Blocked: State corruption detected`.

## 4. Enum de Fases y Triggers

Fases canónicas (usadas por matrix.yaml):

| Fase | Nombre | Equivale a |
|------|--------|-----------|
| `init` | Inicialización del proyecto/workspace | §2 del lifecycle |
| `requirements` | Levantamiento | Fase 1 |
| `planning` | Planificación y contratos | Fase 2 |
| `design` | Exploración de diseño UI | Fase 2.5 (solo UI) |
| `validation` | Validación IA de specs | Fase 3 |
| `decomposition` | Descomposición en tareas | Fase 4 |
| `execution` | Implementación con spec SDD | Fase 5 |
| `execution-no-spec` | Implementación sin spec formal | Fase 5-alt |
| `quality` | Validación de calidad | Fase 6 |
| `gitops` | Integración y promoción | Fase 7 |
| `transversal` | Actúa en cualquier fase | — |

Triggers (no son fases; activan al agente puntualmente):

| Trigger | Significado |
|---------|-------------|
| `post-gate2-regression` | Pruebas E2E de regresión tras aprobar QA |
| `any-failure` | RCA ante fallo en cualquier fase |

Los gates G1/G2 NO son fases: son estados de espera definidos arriba.

## 5. Reglas de Transición

1. Los gates solo se liberan con la firma exacta (sin aliases).
2. `task-decomposer` no inicia si falta el Gate 1; `git-executor` no promociona ramas si falta el Gate 2.
3. Un incremento solo puede estar en UN estado a la vez.
4. Toda transición debe quedar registrada en el shared context con fecha y agente responsable.
5. Self-healing: máximo 3 reintentos autónomos antes de pasar a `blocked` con escape-report.
