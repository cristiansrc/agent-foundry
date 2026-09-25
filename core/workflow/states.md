# Máquina de Estados del SDLC-IA

Fuente de verdad única para los estados del ciclo de vida. Los agentes NO
declaran estados propios: leen y escriben los definidos aquí. Cualquier estado
fuera de este enum es inválido y activa `corrupted-state`.

## 1. Estados del Incremento (Shared Context)

Los estados son compartidos por las tres rutas. En Lite/Standard puede omitirse
la fase de validación SDD formal; las transiciones de calidad y Gate 2 permanecen.
Solo Full pasa por `validated-not-executed` y `awaiting-human-plan-approval`.

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

### Excepción de Gate 1 por nivel

- Full: `verdict: ready` y firma humana exacta antes de descomponer/ejecutar.
- Standard: brief revisado y aprobado explícitamente antes de ejecutar; no
  transita por `awaiting-human-plan-approval` y no requiere `verdict: ready`.
- Lite: petición explícita del usuario o bug reproducible autoriza el alcance
  acotado; no se solicita aprobación de plan separada.
- En todas las rutas, la promoción a ramas estables exige Gate 2. Para Lite, si
  el cambio se promueve, crear un shared context compacto antes de validación QA.

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
| `pre-gate2-regression` | Pruebas E2E de regresión antes de aprobar QA |
| `any-failure` | RCA ante fallo en cualquier fase |

Los gates G1/G2 NO son fases: son estados de espera definidos arriba.

## 5. Reglas de Transición

1. Los gates solo se liberan con la firma exacta (sin aliases).
2. En Full, `task-decomposer` y `executor` no inician si falta Gate 1. Lite/Standard
   usan `architect-executor` conforme a su autorización documentada. `git-executor`
   nunca promociona ramas si falta Gate 2.
3. Un incremento solo puede estar en UN estado a la vez.
4. Toda transición debe quedar registrada en el shared context con fecha y agente responsable.
5. Self-healing: máximo 3 reintentos autónomos antes de pasar a `blocked` con escape-report.

## 6. Handoff Compacto entre Agentes

Toda transferencia de trabajo usa el formato compacto. Prohibido incrustar
diffs completos, logs extensos o código en el shared context: los artefactos
viven en archivos y se referencian por ruta.

| Campo | Regla |
|-------|-------|
| `tarea` | ID estable del task board en Full; en Lite/Standard, ID del brief o referencia corta de la solicitud |
| `estado_destino` | solo valores del enum canónico (§2) |
| `artefactos` | rutas exactas tocadas/generadas, máximo 7 |
| `commit` | SHA corto (≥7) cuando aplique; en la rama de feature del incremento |
| `verificacion` | comando corrido + exit code por suite (sin salida cruda) |
| `nota` | opcional; UNA línea, ≤80 caracteres |

Reglas:

1. Referencia por ruta, nunca contenido incrustado (salvo firmas de gate §3).
2. La verificación declara COMANDO y RESULTADO; el log completo vive en archivo
   o en la sesión, no en el shared context.
3. Cada handoff ocupa ≤15 líneas del shared context.
4. Handoff que viole el formato es hallazgo de proceso para `reviewer`
   (drift de proceso), sin bloquear el flujo funcional salvo que oculte
   verificación exigida.
