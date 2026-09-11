# Runbook: Plugin `model-router` (OpenCode)

Enforcement en runtime del routing `agente → modelo`. Compensa dos límites
de OpenCode sin romper la arquitectura agnóstica de la foundry.

## Por qué existe

1. El `Task` tool no acepta `model` en sus args
   (`description, prompt, subagent_type, task_id, command, background`). Un
   hook `tool.execute.before` sobre `task` no puede inyectar
   `output.args.model`: el schema lo rechazaría.
2. `handleSubtask` (`session/prompt.ts`) pinta el mensaje padre con el modelo
   del primario aunque la sesión hija corra otro modelo. Parece "siempre
   terra" aunque la ejecución sea correcta.

El hook que sí corre en cada sesión —padre e hijas de `Task`— es
`chat.message`, y puede reescribir `output.message.model` antes de guardar.
Eso hace este plugin con una tabla `ROUTING` renderizada desde
`profiles/models.yaml`.

## Fuentes y generados

| Ruta | Rol |
|------|-----|
| `plugins/opencode/model-router/model-router.ts.tmpl` | Template versionado. Solo placeholder `__ROUTING_JSON__`, jamás un ID concreto (lint lo bloquea). |
| `plugins/opencode/model-router/README.md` | Documentación del plugin. |
| `adapters/opencode/out/plugin/foundry-model-router.ts` | Generado por `adapters/shared/render.py::render_plugin()`. No editar a mano. |
| `~/.config/opencode/plugins/foundry-model-router.ts` | Instalado por `tooling/sync.sh`. OpenCode lo autocarga al arrancar (plugins locales). |

Flujo: `profiles/models.yaml` → `build.sh` → `out/plugin/` → `sync.sh` →
`~/.config/opencode/plugins/`. `core/` sigue agnóstico.

## Hooks del plugin

| Hook | Comportamiento |
|------|----------------|
| `chat.message` | Si `input.agent` está en `ROUTING`, parte `provider/model`, compara con `output.message.model` y lo sobrescribe si difiere. Log `foundry-model-router` vía `client.app.log`. Nunca lanza. |
| `tool.execute.before` (tool `task`) | Solo observabilidad: logea qué modelo *debería* usar el `subagent_type` delegado según `ROUTING`. No muta args. |

## Cambiar un modelo

Es el runbook `model-change.md` estándar; el plugin se regenera solo:

```bash
# 1. Solo profiles/models.yaml
# 2. Build (lint + agentes + plugin)
./tooling/build.sh
# 3. Evals del agente afectado (NO opcional)
python3 evals/run.py evals/cases/spec-validator.yaml --executor opencode --model <nuevo-modelo>
# 4. Sync (backup automático de agents/ skills/ plugins/)
echo y | ./tooling/sync.sh
./tooling/status.sh
```

Reinicia OpenCode: config y plugins cargan una sola vez al arrancar.

## Verificar que enruta

```bash
# Generado al día y sin placeholder
grep -c '__ROUTING_JSON__' adapters/opencode/out/plugin/foundry-model-router.ts  # 0
# Instalado == generado
diff adapters/opencode/out/plugin/foundry-model-router.ts ~/.config/opencode/plugins/foundry-model-router.ts
# En OpenCode: delega una tarea y busca en logs el servicio foundry-model-router
# (routing <agente>: <antes> -> <después> / task -> <agente> should run <modelo>)
```

## Rollback

1. `git revert` del commit de `profiles/` → `build.sh` → `sync.sh`.
2. O restaura el backup del sync (incluye `plugins/`):
   `tar -xzf ~/.local/share/agent-foundry/backups/<ultimo>.tar.gz -C ~/.config/opencode`,
   luego reinicia OpenCode.

## Límites conocidos

- Si un ID de `ROUTING` no existe en `/models` (proveedor no conectado), el
  `getModel` fallará con `Model not found`: completa `/connect` antes del
  sync (ver `opencode-harness.md`).
- El plugin no gestiona `variant`: la deja intacta.
- `chatgpt`/`kiro` no usan este plugin: su routing vive en sus propios
  adapters.
