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
4. Solo después instalar en el proyecto destino con `tooling/sync.sh --project <ruta> --apply`.

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
| Review / seguridad / QA final | OpenCode Go | GLM-5.3 | reviewer, security-reviewer, final-validation; sin visión: capturas por functional-tester-agent |
| Validación enterprise | OpenCode Go | GLM-5.3 | enterprise-spec-validator; conservar evaluación separada del implementador |
| Descomposición de tareas | OpenCode Go | DeepSeek V4 Pro | task-decomposer (prioriza razonamiento; evals 4/4 en repeat 3) |
| Gobernanza API / remediación | OpenCode Go | MiMo-V2.6 Pro | api-governance-agent, spec-remediator |
| Código delicado | OpenCode Go | DeepSeek V4 Pro | refactor, database-architect |
| Código y documentación | OpenCode Go | DeepSeek V4.1 Flash | executor, architect-executor, devops-architect, git-executor y documentation (pilotos 2026-10-18/19; documentation-delivery pasa 2/2 casos en repeat 3 frente a MiMo) |
| Tests | OpenCode Go | Claude Haiku 5.5 | test-architect (familia Anthropic, independiente del executor; Kimi K2.7 como rollback manual) |
| Trabajo mecánico | OpenCode Go | MiMo-V2.6 Flash | context-curator |
| Pruebas funcionales UI/E2E | ChatGPT Plus | GPT-6 Luna | functional-tester-agent (3/3 casos; MiMo 0/3 y GLM 1/3 en repeat 2) |
| Implementación UI/E2E | OpenCode Go | MiMo-V2.6 Flash | ui-executor (3/3 casos con MiMo, GLM y Luna en repeat 2) |

El perfil actual reactivó GLM-5.3 para review, seguridad, QA final y validación
enterprise. Planner y Spec Validator comparten Sol por la excepción humana
documentada; roles y dictámenes siguen separados. Cada cambio de binding
requiere evals antes de instalarse.

### Si se agota el allowance de Plus

No hay degradación automática: `fallbacks` en `profiles/models.yaml` es
declarativo y ningún adapter lo consume. Si un agente de Plus falla por cuota,
el error llega al orquestador y hay que cambiar el binding a mano.

Orden de preferencia para recortar sin romper la independencia de validadores:

1. Mueve `ui-designer` a `mimo_v26_flash` en Go (ahorra Luna, no Sol).
2. Reducir alcance/contexto de las consultas y evaluar un modelo alternativo
   disponible, sin cambiar bindings automáticamente.
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
`<proyecto>/.opencode/plugins/` por `sync.sh --project <ruta> --apply`. Detalle en
`docs/runbooks/model-router.md`.

## Sincronización y rollback

`tooling/sync.sh --project <ruta>` muestra la vista previa.
`tooling/sync.sh --project <ruta> --apply` instala el bundle en
`<proyecto>/.opencode/`, conserva claves ajenas de `opencode.json` y
guarda un recibo y backups bajo `<proyecto>/.opencode/backups/`.
Reinicia OpenCode tras instalar; config y plugins cargan al arrancar.
El instalador no autentica proveedores: OAuth se completa por el usuario
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
