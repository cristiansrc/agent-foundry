# Runbook: Plugin `model-router` (OpenCode V2)

Static routing lives in the agent files' `model:` (rendered from
`profiles/models.yaml`); V2 subagents honor it natively. The plugin adds
observability plus optional dynamic agent selection via Jev. It compensates
no V1 limits anymore — it is routing policy + logs, not enforcement.

## Por qué existe (V2)

1. Cada agente renderizado lleva su `model:` en el frontmatter y el subagente
   V2 lo usa nativamente (o hereda el de la sesión padre si no tiene).
2. La selección dinámica de *agente* vía Jev no existe en el core: el plugin
   la aplica reescribiendo el input del tool `subagent` (sucesor V2 de `task`)
   cuando Jev devuelve confianza de auto-route.

## Fuentes y generados

| Ruta | Rol |
|------|-----|
| `plugins/opencode/model-router/model-router.ts.tmpl` | Template versionado con placeholders de routing estático y configuración Jev; los IDs se incrustan únicamente en la salida generada. |
| `plugins/opencode/model-router/README.md` | Documentación del plugin. |
| `adapters/opencode/out/plugin/foundry-model-router.ts` | Generado por `adapters/shared/render.py::render_plugin()`. No editar a mano. |
| `~/.config/opencode/plugins/foundry-model-router.ts` | Instalado por `tooling/sync.sh`. OpenCode lo autocarga al arrancar (plugins locales). |

Flujo: `profiles/models.yaml` → `build.sh` → `out/plugin/` → `sync.sh` →
`~/.config/opencode/plugins/`. `core/` sigue agnóstico.

## Hooks del plugin

| Hook | Comportamiento |
|------|----------------|
| `ctx.tool.hook("execute.before")` (tool `subagent`) | Para los agentes dinámicos consulta Jev con el prompt compacto, valida confianza y puede cambiar el subagente solicitado. Si Jev falla o no hay credencial, conserva el routing estático (modelo del agent file). |
| (observabilidad) | Cada delegación registra `subagent -> <agente> should run <modelo>` en el log del servidor. |

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
# En OpenCode: delega una tarea y busca en el log `[foundry-model-router]`
# (subagent -> <agente> should run <modelo> / jev reroute <a> -> <b>)
```

## Rollback

1. `git revert` del commit de `profiles/` → `build.sh` → `sync.sh`.
2. O restaura el backup del sync (incluye `plugins/`):
   `tar -xzf ~/.local/share/agent-foundry/backups/<ultimo>.tar.gz -C ~/.config/opencode`,
   luego reinicia OpenCode.

## Límites conocidos

- Si un ID de `ROUTING` no existe en `/models` (proveedor no conectado), el
  subagente fallará con `Model not found`: completa `/connect` antes del
  sync (ver `opencode-harness.md`).
- El plugin no gestiona `variant`.
- `chatgpt`/`kiro` no usan este plugin: su routing vive en sus propios
  adapters.
- La selección dinámica requiere `AI_GATEWAY_API_KEY` para Vercel o `JEV_API_KEY`
  para el proveedor oficial. Sin credencial solo funciona el routing estático.
- El contexto disponible en `execute.before` es el prompt de la tarea; el
  contexto autoritativo completo debe haber sido reducido por el orquestador.
- Modelo por nivel de razonamiento Jev no se puede forzar vía hooks V2: el
  subagente corre su modelo del agent file.
