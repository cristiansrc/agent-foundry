# Ciclo de Vida del Desarrollo (SDLC-IA)

Estándar del ciclo de desarrollo gobernado por agentes. Los estados citados
están definidos formalmente en [states.md](states.md); la matriz
agente-fase-skill en [matrix.yaml](matrix.yaml).

## 1. Clasificación de Agentes

- **Workers (obreros):** implementan código, BD, docs e infraestructura.
  `executor`, `architect-executor`, `database-architect`, `devops-architect`,
  `refactor`, `documentation`, `spec-remediator`, `functional-tester-agent`,
  `git-executor`.
- **Consultants (consultores):** asesoran, diseñan y descomponen.
  `requirements-analyst`, `planner`, `enterprise-architect`,
  `solution-architect`, `test-architect`, `task-decomposer`,
  `context-curator`, `master-orchestrator`.
- **Validators (validadores):** solo lectura; auditan calidad y consistencia.
  `spec-validator`, `enterprise-spec-validator`, `api-governance-agent`,
  `bug-diagnostician`, `reviewer`, `security-reviewer`, `final-validation`.
- **Guardrails:** bloquean enrutes accidentales (`general`).
- **Personal (fuera del SDLC):** `hyprmind-orchestrator`,
  `hyprmind-deep-thinker`, `hyprmind-vision-analyst`.

## 2. Inicialización

**Proyecto standalone nuevo:** el `planner` inicializa la Master Spec en
`docs/specs/master_spec.md` y los contratos `openapi.yaml`. Se genera el grafo
de conocimiento del repositorio (graphify) por primera vez.

**Workspace multi-proyecto:** `enterprise-architect` inicializa la Master Spec
global y `docs/specs/workspace_changes.md`; graphify se instala en la raíz de
la solución.

## 3. Flujo Incremental

```
Fase 1 Requerimientos ─► Fase 2 Planificación ─► Fase 3 Validación IA
        │                                              │ verdict ready
        ▼                                              ▼
   GATE HUMANO 1: aprobación de plan (states.md §3)
        │
        ▼
Fase 4 Descomposición ─► Fase 5 Ejecución ─► Fase 6 Calidad
                                                │
                                                ▼
                              GATE HUMANO 2: aprobación QA
                                                │
                                                ▼
                                    Fase 7 Git-Ops (merge y promoción)
```

### Fase 1 — Levantamiento de Requerimientos
- Agente: `requirements-analyst`. Estado: `requirements-discovery`.
- Entregable: `docs/specs/requirements/<increment-name>-requirements-brief.md`.
- Git: se crea `feature/<increment-name>` desde `develop`.

### Fase 2 — Planificación y Contratos
- Agentes: `planner` (consulta a `solution-architect`, `enterprise-architect` y,
  si el incremento tiene superficie UI, a `ui-designer`).
- Estado: `planning`.
- Entregable: Delta Spec `docs/specs/increments/<increment-name>.md` +
  actualización de `openapi.yaml`.

#### Fase 2.5 — Exploración de Diseño UI (solo incrementos con UI)
- Agente: `ui-designer`. Protocolo: skill `ui-design-exploration`.
- Clarificación → 3-4 direcciones como HTML autocontenidos en
  `docs/designs/<increment-name>/` (estático o clickeable) + README comparativo.
- El humano elige dirección (puede mezclar elementos); la elección queda
  registrada en el README y se firma junto al Gate 1.
- La dirección elegida es fuente de verdad para el executor vía skill
  `design-to-code`: prohibido reinterpretar la UI durante implementación.

### Fase 3 — Validación IA
- Agentes: `spec-validator` (+ `enterprise-spec-validator` si hay workspace,
  + `api-governance-agent` si cambian contratos).
- Estado: `validator-review` → `validated-not-executed` o `revision-needed`
  (con ciclo de `spec-remediator` hasta llegar a ready).

### GATE HUMANO 1 — Aprobación de Plan
- Estado: `awaiting-human-plan-approval`. Firma: ver states.md §3.

### Fase 4 — Descomposición
- Agente: `task-decomposer`. Estado: `decomposition-completed`.
- Entregable: `docs/specs/tasks/<increment-name>-task-board.md` en `todo`.

### Fase 5 — Ejecución
- Agentes: `executor` (con spec SDD validada) o `architect-executor` (sin spec),
  con soporte de `test-architect`, `database-architect`, `devops-architect`,
  `refactor` y `documentation`.
- Estados: `in_progress`; tareas `todo → in_progress → done | blocked`.
- Pre-flight obligatorio: compilar, tests locales, graphify update.
- Deuda técnica: registrarla en `technical_debt.md`, nunca ocultarla.
- Self-healing: máximo 3 reintentos antes de `blocked` + escape-report.

### Fase 6 — Validación de Calidad
- Agentes: `reviewer`, `security-reviewer`, `final-validation` y, cuando hay UI,
  `functional-tester-agent` antes del Gate 2. Los validadores reportan; no corrigen
  el mismo cambio que certifican.
- Estado: `validation-review` → `quality-approved`.
- Criterios: cobertura ≥85% por archivo testable, sin bugs críticos,
  sin drift arquitectónico, hallazgos de seguridad resueltos o documentados.

### GATE HUMANO 2 — Aprobación QA
- Estado: `awaiting-human-qa-approval`. Firma: ver states.md §3.
- El humano prueba manualmente o valida la ejecución E2E de
  `functional-tester-agent`.

### Fase 7 — Git-Ops
- Agente exclusivo: `git-executor`. Estados: `merged` → `archived`.
- Promoción: `feature/* → develop → qa → master/main` con PRs y tag semver.

## 4. Políticas Transversales

1. **Aislamiento de proyecto:** prohibido escribir fuera del repo activo.
2. **Placeholder Guard:** `<increment-name>` se resuelve dinámicamente o se pregunta.
3. **Git exclusivo de git-executor:** ningún otro agente ejecuta comandos git.
4. **Inmutabilidad de estado IA:** solo las firmas humanas del states.md §3 son editables por humanos.
5. **Pre-push hook:** los pushes hacia ramas estables exigen el shared context
   del incremento exacto con `quality-approved` + firma del Gate 2 (ver tooling/hooks).
6. **Conventional Commits** con scope del incremento: `feat(<increment>): ...`.
7. **MEMORY.md:** errores resueltos se registran como reglas para prevenir reincidencia.
