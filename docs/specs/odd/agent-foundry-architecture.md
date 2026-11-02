# ODD: agent-foundry-architecture
lane: trivial
origin: docs/specs/.working/foundry-architecture-planning-context.md (pack_status: conflicting; snapshot a865eb0)

## Outcome

Publicar documentación de arquitectura de Agent Foundry que (1) registre el
as-built verificable contra el repositorio, (2) describa la arquitectura
futura/roadmap de integración ChatGPT Desktop/Codex, MCP local multiproyecto y
OpenCode tal como la aportó el usuario (propuesta, no hecho actual),
(3) conserve `master-orchestrator` como orquestador vigente, (4) distinga la
evidencia aportada por el usuario de la reproducible localmente, y (5) incluya
inventario de documentos canónicos a actualizar y límites declarados. Sin
efecto en runtime.

## Evidence

- before: `glob docs/specs/odd/**` → 0 resultados; no existe odd-card. Tampoco
  existe `docs/architecture.md` ni `docs/adr/` (`ls docs/adr` → ausente). En
  `docs/specs/` solo hay `.working/foundry-architecture-planning-context.md`.
- after: `docs/specs/odd/agent-foundry-architecture.md` existe con
  `lane: trivial` y las secciones Outcome/Evidence/Signals/Boundaries/Escalation
  completas (esta entrega). En la fase documental posterior: los documentos
  objetivo existen, cada afirmación cita fuente (pack o repositorio) y el scan
  de secretos del delta queda limpio.

## Signals (opcional en trivial)

- N/A: sin cambio de comportamiento en runtime. Verificación asociada:
  spot-check de las referencias `[path:línea]` citadas y `gitleaks`
  (filesystem) sobre los archivos nuevos.

## Boundaries

- touches:
  - `docs/specs/odd/agent-foundry-architecture.md` (esta tarjeta).
  - Fase documental posterior, solo prosa y fuera de bloques generados:
    `README.md` (prosa fuera de `BEGIN/END:GENERATED-TABLES`) y `PLAN.md`,
    ambos autorizados explícitamente por la petición del usuario.
    `AGENTS.md`, `docs/runbooks/mcps.md`, `docs/runbooks/opencode-harness.md`,
    `docs/runbooks/model-router.md`,
    `docs/runbooks/chatgpt-opencode-phase1.md`,
    `docs/runbooks/chatgpt-opencode-phase2.md`,
    `docs/runbooks/chatgpt-opencode-phase15-results.md`,
    `docs/runbooks/agent-operations.md`,
    `docs/runbooks/chatgpt-desktop-skills.md` (presente en el repo; no listado
    en el pack).
  - Nuevos `docs/architecture.md` y `docs/adr/**` autorizados explícitamente por
    la petición del usuario (antes condicionados a la pregunta abierta 2 del
    pack): la arquitectura futura se documenta allí como propuesta, y los ADRs
    solo registran decisiones ya tomadas o la propuesta etiquetada como tal.
    Runbooks adicionales de `docs/runbooks/` quedan autorizados únicamente si
    la petición los requiere; ninguno se crea ni edita en este turno.
- must-not-touch: código, tests, configs, `profiles/**`, `core/**` (agentes y
  skills), `adapters/*/out/**`, bloques `GENERATED-TABLES`,
  `tooling/gen-readme.py`, credenciales/`.opencode/`/`.venv/`, Entralo, Git
  mutante o commits, y los ítems 1-8 del inventario del pack (respaldo SQLite +
  launcher del puente). Los ítems 9-12 (huérfanos) no se restauran ni eliminan
  en esta tarea.

## Inventario de docs canónicos (transcrito del pack, existencia verificada)

| Documento | Rol actual | Acción documental esperada | Verificación |
|---|---|---|---|
| `README.md` | Visión, arquitectura de datos, tablas generadas | Alinear prosa (C2, C4, C7); no tocar bloques `GENERATED-TABLES` | `[README.md:34-49,106-111,195-202,206,236,242,407,474]` |
| `AGENTS.md` | Convenciones y estructura del repo | Alinear estructura real (`sdlc/` + `installer/` vacío; sin `personal/`) | `[AGENTS.md:39]` (C4) |
| `PLAN.md` | Decisiones y fases | Marcar fases ya implementadas (C5, C6) sin reabrir decisiones | `[PLAN.md:31,149-152]` |
| `docs/runbooks/mcps.md` | MCP, visión retirada | Corregir bindings obsoletos (C3) | `[docs/runbooks/mcps.md:28-34]` |
| `docs/runbooks/opencode-harness.md` | Harness recomendado y reparto por facturación | Mantener como decisión cerrada | `[docs/runbooks/opencode-harness.md:16-24]` |
| `docs/runbooks/model-router.md` | Routing runtime | Mantener; sin hardcodear modelos | pack (`Decisions locked`) |
| `docs/runbooks/chatgpt-opencode-phase1.md` | Puente ChatGPT↔OpenCode fase 1 | Actualizar alcance y límites del puente | pack §Impact map |
| `docs/runbooks/chatgpt-opencode-phase2.md` | Fase 2 (launcher, respaldo de historial) | Documentar incluyendo secciones locales no committeadas | `[docs/runbooks/chatgpt-opencode-phase2.md:42-104,140-164]` |
| `docs/runbooks/chatgpt-opencode-phase15-results.md` | Resultados de fase 1.5 | Mantener como evidencia histórica | pack §Impact map |
| `docs/runbooks/agent-operations.md` | Operación de agentes | Alinear con carriles ODD y gates | pack §Impact map |
| `docs/runbooks/chatgpt-desktop-skills.md` | Skills desktop-only del adapter ChatGPT | Alinear con el inventario de skills y su instalación | `[docs/runbooks/chatgpt-desktop-skills.md:1-45]` |
| `docs/investigations/*.md` (5) | Contexto futuro, no norma | Citar como investigación; no elevar a norma | `[AGENTS.md:47]` |

Fuentes que alimentan la doc pero no se editan: `profiles/*.yaml` (autoridad de
bindings), `core/**`, `tooling/gen-readme.py` (dueño de las tablas del README).

## Evidencia: aportada por usuario vs reproducible local

- Aportada por la solicitud del orquestador (no verificada por herramientas en
  este turno): carril `trivial`; objetivo de documentar as-built + roadmap;
  ChatGPT Desktop y Codex CLI como clientes separados; MCP local multiproyecto
  como objetivo; diseño explícito del control plane y del roadmap aportado por
  el usuario como propuesta; preservar `master-orchestrator`; inventariar docs
  y límites.
- Reproducible y comprobada en este turno: ausencia de `docs/specs/odd/**` y de
  `docs/adr/` (`glob`, `ls`); existencia de los 11 documentos y de
  `docs/investigations/` (`ls`); ubicación del orquestador en
  `core/agents/sdlc/consultants/master-orchestrator.md` (`find`); contenido del
  pack y de `docs/runbooks/chatgpt-desktop-skills.md:1-45` (`read`).
- Reproducible pero no ejecutada en este turno (requiere rol con shell y no
  forma parte de este alcance): `git status`/`git diff`, `./tooling/lint.sh`,
  `python3 tooling/audit_matrix.py`, `./tooling/build.sh`, `evals/run.py`.
  `build.sh` no se ejecutó a propósito: regenera `adapters/*/out/`, que esta
  tarea no debe mutar.

### Entrada del usuario sobre la arquitectura futura (propuesta, no verificada localmente)

Los siguientes puntos provienen de la petición del usuario. Se registran como
diseño/objetivo declarado, no como estado actual ni como hallazgo del repo:

- **Clientes separados:** el usuario define **ChatGPT Desktop** y **Codex CLI**
  como dos clientes distintos de la misma integración. La documentación futura
  debe tratarlos por separado y no asumir que `adapters/chatgpt/out/` (que el
  pack asocia a Codex) describe a ambos.
- **Objetivo multiproyecto:** el usuario fija como objetivo el MCP local
  **multiproyecto** (un mismo MCP local sirviendo varios proyectos). Lo
  verificable hoy son solo el puente loopback-only de solo lectura
  (`tooling/opencode_bridge.py`) y el MCP stdio project-scoped
  (`tooling/opencode_mcp.py`); la operación simultánea multiproyecto es
  objetivo, no capacidad demostrada.
- **Diseño del control plane y roadmap:** el usuario aporta explícitamente el
  diseño requerido del control plane y las fases del roadmap. En la fase
  documental se transcriben como **propuesta/roadmap** (p. ej. en
  `docs/architecture.md`) y nunca como arquitectura implementada. El detalle se
  toma de la petición del usuario; no se reconstruye de memoria ni se completa
  por inferencia.

## Límites y pendientes de verificación

- Estado del working tree derivado contra HEAD `a865eb0` sin `git status`;
  distinción staged/unstaged no verificable (pack §Límites de evidencia).
  Conservar intactos los ítems 1-8 del inventario.
- Contradicciones C1-C7 abiertas: la documentación nueva debe contar agentes y
  skills desde `core/` (no desde `out/`) y tomar `profiles/*.yaml` como
  autoridad sobre cualquier prosa.
- Pendiente único de verificación: contrastar cada fase del roadmap aportado con
  evidencia local concreta (código, runbooks, tests) antes de afirmarla como
  implementada. Comprobado en este turno: `docs/architecture.md` y `docs/adr/`
  siguen ausentes (`ls`), por lo que ningún documento nuevo respalda aún esas
  fases; lo que no tenga evidencia local se publica etiquetado como propuesta.
- La arquitectura futura (clientes separados, MCP multiproyecto, control plane)
  no se valida localmente en este turno y se etiqueta como propuesta del
  usuario; no se usa para describir el estado actual.

## Registro de carril

`## Lane: trivial` no se registró en shared context: no existe shared context
en el repo en este momento (`docs/specs/.working/` solo contiene el pack). No se
registra aprobación alguna.

## Escalation

Vacío para el alcance documental: el pack declara "Bloqueos: ninguno para
carril trivial de documentación". Ante cualquier disparador de §2 (contratos,
esquema de BD, auth, módulo o dependencia nueva, decisión de negocio,
boundaries excedidos) → `Blocked: escalate-to-sdd`.
