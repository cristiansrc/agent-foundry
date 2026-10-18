# OpenCode como Harness — routing y conexión

OpenCode es el único harness: concentra agentes, skills, permisos, MCPs y
hooks. La inferencia se divide entre dos suscripciones, no entre dos flujos de
trabajo distintos.

## Conexiones requeridas

1. En OpenCode, ejecutar `/connect` y autenticar **OpenAI → ChatGPT
   Plus/Pro**.
2. Confirmar con `/models` que aparecen `openai/gpt-6-luna` y
   `openai/gpt-6.1-sol`. Si no aparecen, la suscripción no cubre el modelo.
3. Conectar o conservar **OpenCode Go** y confirmar sus modelos con `/models`.
4. Solo después instalar con `tooling/sync.sh`.

Desde 2026-10-03 ChatGPT Plus reemplaza a Copilot Pro+ (`harness_copilot`
queda inactivo como rollback). El motivo es la forma de facturar: Copilot Pro+
cobra **por token** en AI Credits (Pro+ = 7000/mes ≈ $70) y se consumió el 90%
en una semana; ChatGPT Plus da un **allowance de Codex** con dos medidores —
ventana de 5h y tope semanal— compartido entre Work y Codex.

Privacidad: los planes personales de ChatGPT pueden entrenar con tus prompts
por defecto (opt-out en los ajustes de la cuenta); OpenCode Go tiene ZDR en los
modelos donde importa. Si eso es unacceptable, mueve el agente sensible a Go.

## Política de routing

Regla que decide cada caso: **Sol es el recurso escaso de Plus y Luna el
abundante** (15-160 vs 350-3.000 mensajes por 5h). Sol queda solo para
razonamiento que decide; el volumen nunca lo toca. OpenCode Go topa **por
modelo**, así que cada familia tiene contador propio y no compite con Plus.

| Capacidad | Suscripción | Modelo | Agentes |
|---|---|---|---|
| Orquestación | ChatGPT Plus | GPT-6 Luna | master-orchestrator, general |
| UI / diseño | ChatGPT Plus | GPT-6 Luna | ui-designer (iterativo y con visión) |
| Planificación | ChatGPT Plus | GPT-6.1 Sol (effort high) | planner |
| Patrones / diseño técnico | ChatGPT Plus | GPT-6.1 Sol | solution-architect |
| RCA | ChatGPT Plus | GPT-6.1 Sol | bug-diagnostician, requirements-analyst |
| Validación crítica | ChatGPT Plus/Pro | GPT-6.1 Sol | spec-validator (excepción temporal de familia aprobada2026-10-11) |
| Macro-arquitectura | ChatGPT Plus/Pro | GPT-6.1 Sol | enterprise-architect |
| Review / seguridad / QA final | OpenCode Go | LongCat-2.0 | reviewer, security-reviewer, final-validation (familia Meituan, independiente de planner, spec-validator y executor; sin visión: delegan capturas) |
| Validación enterprise | OpenCode Go | LongCat-2.0 | enterprise-spec-validator (misma independencia triple; Kimi K3 como rollback manual) |
| Plan estructurado / remediación | OpenCode Go | MiMo-V2.6 Pro | task-decomposer, api-governance-agent, spec-remediator |
| Código delicado | OpenCode Go | DeepSeek V4 Pro | refactor, database-architect |
| Código | OpenCode Go | DeepSeek V4.1 Flash | executor, architect-executor, devops-architect, git-executor (piloto 2026-10-18) |
| Tests | OpenCode Go | Claude Haiku 5.5 | test-architect (familia Anthropic, independiente del executor; Kimi K2.7 como rollback manual) |
| Trabajo mecánico | OpenCode Go | MiMo-V2.6 Flash | documentation, context-curator |
| UI/E2E | OpenCode Go | MiMo-V2.6 Flash | functional-tester-agent, ui-executor |

GLM-5.3 normal está pausado por petición humana2026-10-11 debido al consumo.
Sus dos agentes pasan a Sol6.1; Planner/Spec Validator comparten familia/modelo
temporalmente, con roles e informes separados. LongCat se conserva en review,
seguridad, calidad y validación enterprise. No volver automáticamente a GLM
como rollback; una alternativa requiere decisión y evaluación explícitas.

### Si se agota el allowance de Plus

No hay degradación automática: `fallbacks` en `profiles/models.yaml` es
declarativo y ningún adapter lo consume. Si un agente de Plus falla por cuota,
el error llega al orquestador y hay que cambiar el binding a mano.

Orden de preferencia para recortar sin romper la independencia de validadores:

1. Mueve `ui-designer` a `mimo_v26_flash` en Go (ahorra Luna, no Sol).
2. Reducir alcance/contexto de las consultas y evaluar un modelo alternativo
   disponible, sin reactivar GLM pausado automáticamente.
3. Como último recurso, baja el `variant` del `planner` de `high` a `medium`.

La revisión sigue siendo por otro rol y exige evidencia/gates. Otra familia
es preferencia de diversidad, temporalmente exceptuada por el usuario; no es
garantía suficiente de calidad ni motivo para impedir esta sustitución.

Bloqueados: GPT-6 Astra (opción Pro, no incluida en Plus), modelos preview,
`Omen Alpha` y variantes Muse Spark Contributor (entrenan con prompts).

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
