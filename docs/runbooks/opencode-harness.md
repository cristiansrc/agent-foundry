# OpenCode como Harness — routing y conexión

OpenCode es el único harness: concentra agentes, skills, permisos, MCPs y
hooks. La inferencia se divide entre dos suscripciones, no entre dos flujos de
trabajo distintos.

## Conexiones requeridas

1. En OpenCode, ejecutar `/connect` y autenticar **OpenAI → ChatGPT Plus/Pro**.
2. Confirmar con `/models` que aparecen los IDs configurados para `openai`.
3. Conectar o conservar **OpenCode Go** y confirmar sus modelos con `/models`.
4. Solo después instalar con `tooling/sync.sh`.

Los IDs `openai/gpt-5.6-luna` y `openai/gpt-5.6-terra` son nombres de binding
esperados. Si `/models` muestra un ID diferente, se actualiza
`profiles/models.yaml` antes de usar agentes que dependan de ChatGPT OAuth.

## Política de routing

| Capacidad | Suscripción | Modelo principal | Uso |
|---|---|---|---|
| Orquestación | ChatGPT OAuth | Terra | master-orchestrator; decisiones y delegación con contexto global |
| Razonamiento normal | ChatGPT OAuth | Luna | planner, validación SDD y validación final |
| Razonamiento crítico | ChatGPT OAuth | Terra | arquitectura, seguridad y RCA complejos |
| Plan estructurado | OpenCode Go | LongCat 2.0 | task decomposition y gobernanza API normal |
| Código | OpenCode Go | DeepSeek V4 Flash | executor y migraciones de datos |
| Trabajo mecánico | OpenCode Go | MiMo-V2.5 | orquestación ligera, Git, docs y review normal |
| Código de volumen | OpenCode Go | DeepSeek V4.1 Flash | testing y plataforma |
| UI/E2E | OpenCode Go | DeepSeek V4 Flash Vision Exp | pruebas funcionales con captura |

`Omen Alpha` y las variantes Muse Spark Contributor están bloqueados por
política de privacidad. Estas últimas permiten usar prompts y completions para
entrenar modelos. Luna no se consume desde OpenCode Go: entra únicamente por
la conexión OAuth de ChatGPT.

## Agentes desplegados

El harness instala un agente principal: `master-orchestrator`. Los demás se
instalan como subagentes para que el selector principal no se llene de roles.

- Núcleo: `planner`, `task-decomposer`, `executor`, `reviewer`,
  `final-validation`, `git-executor`.
- Bajo demanda: arquitectura, datos, plataforma, seguridad, UI/E2E,
  documentación, diagnóstico y curación de contexto.
- No desplegados: `general`, `architect-executor`, `requirements-analyst`,
  `refactor` y los perfiles personales HyprMind. Se conservan como histórico o
  perfiles separados, pero no forman parte del SDLC normal.

## Sincronización y rollback

`tooling/sync.sh` hace backup antes de reemplazar `agents/` y `skills/`, y
fusiona únicamente `default_agent` en `opencode.json`: no borra MCPs ni
proveedores existentes.

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
