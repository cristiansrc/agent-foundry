# OpenCode como Harness — routing y conexión

OpenCode es el único harness: concentra agentes, skills, permisos, MCPs y
hooks. La inferencia se divide entre dos suscripciones, no entre dos flujos de
trabajo distintos.

## Conexiones requeridas

1. En OpenCode, ejecutar `/connect` y autenticar **GitHub Copilot** (Pro+).
2. Confirmar con `/models` que aparecen los IDs `github-copilot/...` configurados.
3. Conectar o conservar **OpenCode Go** y confirmar sus modelos con `/models`.
4. Solo después instalar con `tooling/sync.sh`.

Desde 2026-09-30 Copilot Pro+ reemplaza a ChatGPT OAuth (`harness_chatgpt`
queda inactivo como rollback). Copilot factura por tokens en AI Credits
(Pro+ = 7000/mes ≈ $70); OpenCode Go aplica topes **por modelo** (5h = 20% del
mensual). Por eso Copilot solo carga razonamiento que decide y Go el volumen.

Privacidad: Copilot individual puede usar datos para entrenamiento salvo
opt-out en *Copilot settings*; Business/Enterprise está cubierto por DPA.

## Política de routing

| Capacidad | Suscripción | Modelo | Agentes |
|---|---|---|---|
| Orquestación | Copilot | GPT-6 Luna | master-orchestrator, general |
| Planificación | Copilot | GPT-6.1 Sol (high) | planner |
| Requisitos / RCA | Copilot | GPT-6.1 Sol | requirements-analyst, bug-diagnostician |
| Validación crítica / macro-arquitectura | Copilot | Claude Opus 5.5 | spec-validator, enterprise-architect (familia distinta al planner) |
| Patrones / UI / seguridad / validación final | Copilot | Claude Sonnet 5.5 | solution-architect, ui-designer, security-reviewer, final-validation |
| Validación enterprise | OpenCode Go | Kimi K3 | enterprise-spec-validator |
| Plan estructurado / remediación | OpenCode Go | MiMo-V2.6 Pro | task-decomposer, api-governance-agent, spec-remediator |
| Review | OpenCode Go | GLM-5.3 | reviewer (familia distinta a quien codifica) |
| Código delicado | OpenCode Go | DeepSeek V4 Pro | refactor, database-architect |
| Código | OpenCode Go | DeepSeek V4.1 Flash | executor, architect-executor, test-architect, devops-architect |
| Trabajo mecánico | OpenCode Go | MiMo-V2.6 Flash | git-executor, documentation, context-curator |
| UI/E2E | OpenCode Go | DeepSeek V4 Flash Vision Exp (excepción documentada) | functional-tester-agent, ui-executor |

Bloqueados: GPT-6 Astra (coste), modelos preview, `Omen Alpha` y variantes
Muse Spark Contributor (entrenan con prompts).

## Agentes desplegados

El harness instala un agente principal: `master-orchestrator`. Los demás se
instalan como subagentes para que el selector principal no se llene de roles.

- Núcleo: `planner`, `task-decomposer`, `executor`, `ui-executor` (solo
  incrementos con UI aprobada), `reviewer`, `final-validation`, `git-executor`.
- Bajo demanda: arquitectura, datos, plataforma, seguridad, UI/E2E,
  documentación, diagnóstico y curación de contexto.
- No desplegados: `general`, `architect-executor`, `requirements-analyst` y
  `refactor`. Se conservan como histórico o perfiles separados, pero no forman
  parte del SDLC normal.

## Enforcement de routing: plugin `model-router`

El `Task` tool no acepta `model` en sus args, así que el routing se fuerza en
el hook `chat.message` (corre en cada sesión, incluidas las hijas de `Task`).
Fuente: `plugins/opencode/model-router/`; generado:
`adapters/opencode/out/plugin/foundry-model-router.ts`; instalado en
`~/.config/opencode/plugins/` por `sync.sh`. Detalle en
`docs/runbooks/model-router.md`.

## Sincronización y rollback

`tooling/sync.sh` hace backup antes de reemplazar `agents/`, `skills/` y
`plugins/foundry-model-router.ts`, y fusiona únicamente `default_agent` en
`opencode.json`: no borra MCPs ni proveedores existentes. Reinicia OpenCode
tras cada sync (config y plugins cargan al arrancar).

Para cambiar la ruta de backups:

```bash
AGENT_FOUNDRY_BACKUP_DIR=/ruta/escribible tooling/sync.sh
```

El sync nunca autentica proveedores: OAuth siempre se completa por el usuario
en `/connect`.

## Skills para ChatGPT Desktop

Estas dos skills también se pueden instalar en el entorno global de Codex para
que ChatGPT Desktop las descubra en cualquier proyecto:

```bash
tooling/build.sh
tooling/sync-chatgpt.sh
```

El instalador solo reemplaza `project-context-navigation` y
`documentation-reconciliation` dentro de `~/.codex/skills`; no toca OpenCode,
MCPs ni las demás skills.
