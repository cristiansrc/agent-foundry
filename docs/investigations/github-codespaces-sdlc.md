# Investigación: ciclo de vida SDD con agentes sobre GitHub + Codespaces

Fecha: 2026-09-30. Estado: **investigación** (sin implementar).
Objetivo: que cualquier desarrollador (interno o proveedor) trabaje sí o sí
bajo el ciclo de vida de agent-foundry, con aprobaciones de arquitecto y
funcional vía comentarios de GitHub, estados no saltables y flujo bloqueado
sin vistos buenos.

## 1. Conclusión anticipada

Es viable, en 3 fases. La idea clave: **el enforcement vive en el repo
(Actions + rulesets), no en la máquina del desarrollador**. No se puede
obligar técnicamente a "usar los agentes", pero sí se puede rechazar todo
artefacto que no haya pasado por el ciclo (estados, odd-cards, specs, firmas).
Si el camino fácil (Codespace con agentes preinstalados) es también el único
camino que mergea, el resultado práctico es el mismo.

Principio de diseño: **gates deterministas, agentes solo para razonar**.
Las aprobaciones las valida código, nunca un LLM.

## 2. Hallazgos (verificados 2026-09-30)

### 2.1 Rulesets: el candado del flujo

Los rulesets reemplazan a la branch protection clásica y dan lo necesario:

- **Required status checks / required workflows**: `validate-states.py`
  (ya existe en `tooling/`) corre como check requerido en cada PR. Sin
  estados válidos y firmas exactas, no hay merge.
- **Require review from specific teams** (GA nov-2025): exige N aprobaciones
  de un team concreto por patrones de archivo. Permite p. ej. "2 aprobaciones
  de `@org/architects` para `docs/specs/**` y `openapi.yaml`". Complementa a
  CODEOWNERS sin reemplazarlo.
- **Merge queue**: serializa merges a `develop/qa/main` con checks verdes.
- **Bypass**: configurable por rol; en este diseño nadie lo tiene salvo
  emergencia auditada (todo bypass queda en el audit log).
- Fuente: docs de GitHub (available-rules-for-rulesets), changelog 2025-11-03.

### 2.2 Aprobaciones por comentario (ChatOps)

Dos caminos:

- **Clásico determinista**: `peter-evans/slash-command-dispatch` (MIT, 700+
  estrellas) convierte `/approve plan` en `repository_dispatch`. Un workflow
  propio valida team del autor vía API y transcribe la firma. Determinista,
  auditable, sin LLM en el medio.
- **Agentic Workflows (`gh-aw`, public preview)**: trigger `on: slash_command`
  con `on.roles` (solo ciertos permisos disparan) y contexto sanitizado
  anti-inyección. Potente para *despachar agentes*, excesivo para registrar
  una aprobación.

Recomendación: aprobaciones con el camino clásico; `gh-aw` solo en fase 3
para despacho de agentes.

### 2.3 Copilot coding agent (el ejecutor nativo)

Asignar un issue a Copilot → trabaja en entorno Actions → abre draft PR:

- Tratado como **outside collaborator**: sus PRs requieren aprobación humana
  con write antes de que corran los workflows. Encaja con el modelo de gates.
- **No puede aprobar ni mergear**; no puede marcar ready-for-review.
- Commits co-firmados por quien asignó la tarea (trazabilidad).
- Límites: 1 PR por tarea, solo dentro del mismo repo, no retoma PRs ajenos.
- Consume AI credits del que asigna + minutos de Actions.
- Fuente: docs de GitHub (about-coding-agent), changelog 2025-09-25 (GA).

### 2.4 Copilot CLI en Actions con GITHUB_TOKEN (2026-07)

- Sin PAT: el workflow autentica con el `GITHUB_TOKEN` built-in + permiso
  `copilot-requests: write`; flag `--yolo -p` para modo no interactivo.
- En repos de organización el consumo se factura **a la organización**
  (requiere policy "Allow use of Copilot CLI billed to the organization").
- GitHub recomienda Agentic Workflows sobre invocar el CLI crudo.
- Implicación: los validadores automáticos (spec-validator, reviewer) pueden
  correr como checks sin credenciales de usuario. Requiere plan
  Business/Enterprise para facturación a org.
- Fuente: docs (copilot-cli-in-github-actions), changelog 2026-07-02.

### 2.5 Agentic Workflows (`gh-aw`, public preview)

- Workflows en Markdown + frontmatter → compilan a `.lock.yml` ejecutable.
- Motores: Copilot (default), Claude, Codex, Gemini, Pi. **OpenCode existe
  solo como sample no oficial, sin compromiso de compatibilidad.**
- Aporta sandbox, safe-outputs (escrituras validadas en jobs separados),
  presupuestos de AI credits por run, filtrado anti-inyección y `gh aw audit`.
- Implicación: si los agentes foundry deben correr en CI con sus prompts
  exactos, el camino es Copilot CLI crudo o contenedor con OpenCode + secretos
  de entorno, no `gh-aw` con motor Copilot (perdería los prompts/matrix).
- Fuente: github/gh-aw, docs de engines (2026).

### 2.6 Environments: aprobaciones con dientes

- **Required reviewers** (hasta 6 personas/teams) + **prevent self-review**:
  el job se pausa hasta que alguien autorizado aprueba. Un proveedor no puede
  autoaprobarse aunque esté en el team.
- **Secrets de entorno solo disponibles tras la aprobación**: la llave de
  OpenCode Go y credenciales sensibles viven aquí, no en secrets del repo.
- En repos privados requiere plan Team/Enterprise (Business lo cubre).
- Fuente: docs (deployments-and-environments).

### 2.7 Codespaces: el IDE en la nube

- `devcontainer.json` puede preinstalar OpenCode + `tooling/sync.sh`
  (agentes, skills, plugin) vía `postCreateCommand`; **prebuilds** lo dejan
  listo en segundos.
- Cada desarrollador usa **su propio seat** de Copilot (individual Pro+ para
  empezar, Business al escalar): encaja con "comenzar con la suscripción de
  github copilot".
- Acceso a Codespaces exige write en el repo: los proveedores trabajan en
  **forks** (Codespace sobre su fork) o ramas con permisos acotados; jamás
  tocan ramas estables (las protegen los rulesets igual).
- Costo: cómputo por minuto + almacenamiento; los prebuilds también facturan.

## 3. Diseño propuesto

### Fase 0 — Base (sin código de agentes)

- Org + teams: `developers`, `providers` (outside collaborators),
  `architects`, `functional`, `maintainers`.
- Environments: `plan-approval` (reviewers: architects),
  `qa-approval` (reviewers: functional + prevent self-review),
  `agent-keys` (guarda OPENCODE_GO_KEY; reviewers: maintainers).
- CODEOWNERS: `docs/specs/**` y `openapi.yaml` → architects.

### Fase 1 — Enforcement (el repo manda)

Nada corre agentes todavía; todo lo que entra al repo pasa el ciclo:

1. **Check requerido `sdd-states`**: `validate-states.py` sobre el PR
   (nota: el runner necesita `pip install pyyaml`). Falla si hay estados
   saltados, firmas mal formadas o gates sin firmar.
2. **Action `/approve`**: `issue_comment` → verifica team del autor →
   transcribe al shared context
   `## Human Plan Approval: approved_by_user (by @u, 2026-10-..)`.
3. **Check requerido `approval-proof`**: anti-falsificación — ante cada firma
   en el diff, consulta la API de comentarios y exige un `/approve`
   correspondiente de un usuario del team. Una firma escrita a mano sin
   comentario real no mergea.
4. **Rulesets**: checks 1 y 3 requeridos en `develop/qa/main`; review de
   architects por patrones; merge queue; sin bypass salvo maintainers.
5. Carriles con exigencia distinta (reusa `lanes` de `matrix.yaml`):
   `trivial` (CODEOWNERS), `fix` (reviewer + `/approve qa`),
   `feature/workspace` (`/approve plan` + `/approve qa` + checks).

Cambios a este repo para fase 1: formato de firmas con autoría
(`states.md §3`), `validate-states.py` aceptando el sufijo `(by @..)` y el
check `approval-proof`, y workflows de ejemplo en `.github/` (plantilla,
no activos aquí).

### Fase 2 — Validadores automáticos como checks

`spec-validator`, `reviewer`, `gitleaks` corren en cada PR con Copilot CLI +
GITHUB_TOKEN (facturación a la org). Sus veredictos son checks informativos
al inicio y requeridos cuando estabilicen. Los humanos siguen firmando.

### Fase 3 — Agentes bajo demanda

- `/sdd implement` (issue con Gate 1 firmado) → job con OpenCode headless
  (`opencode run --agent executor`, como ya hace `evals/run.py`) o Copilot
  CLI, con secretos del environment `agent-keys`.
- Backlog menor (`trivial`): asignar el issue al coding agent nativo.
- `gh-aw` solo si se necesita su sandbox/auditoría; no para los gates.

## 4. Decisiones abiertas

1. **Identidad que paga CI**: usuario-máquina con seat vs facturación a la
   org (requiere Business/Enterprise + policy).
2. **Tracker del incremento**: Issue (recomendado: ahí van los `/approve`),
   con el shared context como fuente de verdad en el repo.
3. **Secuencia**: fase 1 primero (recomendado) o todo junto.

## 5. Riesgos

- **Prompt injection**: los issues/comentarios son input no confiable. Las
  aprobaciones son deterministas (sin LLM); los agentes que lean issues
  necesitan instrucciones de desconfianza (ya existe `secret-scanning`;
  falta regla equivalente para issues).
- **Outside collaborator**: los PRs del coding agent y de forks no corren
  workflows hasta aprobación — el diseño ya lo asume (Gate 2 existe igual).
- **`gh-aw` en preview** y OpenCode sin motor oficial: no basar los gates
  en ellos.
- **Costos**: Actions minutes + Codespaces compute + AI credits por run
  automático; poner presupuestos (`gh aw audit` o budgets de GitHub) antes
  de fase 2/3.

## 6. Fuentes

- Docs GitHub: available-rules-for-rulesets; changelog required-review-teams
  (2025-11-03); about-coding-agent; copilot-cli-in-github-actions;
  changelog GITHUB_TOKEN (2026-07-02); deployments-and-environments.
- github/gh-aw (repo + docs engines/setup); peter-evans/slash-command-dispatch.
