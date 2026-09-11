# Plugin `model-router` (OpenCode)

Enforces per-agent model routing at runtime. Source of truth stays in
`profiles/models.yaml`; this folder holds only the template. The generated
artifact lives in `adapters/opencode/out/plugin/foundry-model-router.ts`
(never edit `out/` by hand).

## Why it exists

OpenCode's `Task` tool schema has **no `model` field**
(`description, prompt, subagent_type, task_id, command, background` only), so a
`tool.execute.before` hook cannot inject `output.args.model` — it would be
rejected. And `handleSubtask` in `session/prompt.ts` shows the parent model on
the assistant message even when the child session runs the right model, which
looks like "always terra".

The enforceable hook is `chat.message`: every session (parent or subtask
child) creates its user message through it, and the hook can rewrite
`output.message.model` before the message is saved. That is what this plugin
does, using a `ROUTING` table rendered at build time from `profiles/`.

## Data flow

```
profiles/models.yaml (tiers + tier_bindings, única fuente)
  -> adapters/shared/render.py::render_plugin() (resuelve binding por agente)
  -> adapters/opencode/out/plugin/foundry-model-router.ts (ROUTING embebido)
  -> tooling/sync.sh (~/.config/opencode/plugins/foundry-model-router.ts)
```

`core/` stays model-agnostic. The template contains only the
`__ROUTING_JSON__` placeholder — never a concrete `provider/model` ID
(lint enforces this).

## Hooks

| Hook | What it does |
|------|--------------|
| `chat.message` | If `input.agent` is in `ROUTING`, splits `provider/model` and overwrites `output.message.model` when it differs. Never throws; logs via `client.app.log`. |
| `tool.execute.before` (tool `task`) | Observability only: logs which model the named `subagent_type` *should* get per `ROUTING`. Does not mutate args (schema has no `model`). |

## Change a model

1. Edit only `profiles/models.yaml` (see `docs/runbooks/model-change.md`).
2. `./tooling/build.sh` (regenerates agents + plugin).
3. `echo y | ./tooling/sync.sh` (installs agents + skills + plugin).
4. Restart OpenCode (config + plugins load once at startup).
