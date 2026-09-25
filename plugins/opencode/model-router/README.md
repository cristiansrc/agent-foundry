# Plugin `model-router` (OpenCode)

Enforces per-agent model routing at runtime. Source of truth stays in
`profiles/models.yaml`; this folder holds only the template. The generated
artifact lives in `adapters/opencode/out/plugin/foundry-model-router.ts`
(never edit `out/` by hand).

## Why it exists (V2)

V2 subagents natively use their agent file's `model:` (rendered from
`ROUTING`), so static enforcement via message rewriting is obsolete — there
is no V2 equivalent of the V1 `chat.message` model override. This plugin
keeps two jobs:

1. Observability: log which model each `subagent` invocation *should* get.
2. Jev dynamic selection: rewrite the requested subagent when Jev returns an
   auto-route decision (`ctx.tool.hook("execute.before")` on tool `subagent`,
   the V2 successor of V1 `task`). Without a Jev credential only static
   routing applies.

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

## Hooks (V2 API — `export default { id, setup }`, zero imports)

The generated artifact must not import `@opencode/plugin`: the package is
not resolvable from `~/.config/opencode/plugins/`, so any import fails the
load. A plain `{ id, setup }` object satisfies the V2 loader.

| Hook | What it does |
|------|--------------|
| `ctx.tool.hook("execute.before")` (tool `subagent`) | For dynamic agents, asks Jev and rewrites the requested subagent on auto-route confidence; otherwise logs static `ROUTING` expectation. Never throws. |

## Change a model

1. Edit only `profiles/models.yaml` (see `docs/runbooks/model-change.md`).
2. `./tooling/build.sh` (regenerates agents + plugin).
3. `echo y | ./tooling/sync.sh` (installs agents + skills + plugin).
4. Restart OpenCode (config + plugins load once at startup).
