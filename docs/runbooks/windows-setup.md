# Runbook: Instalación en Windows + OpenCode V2

Procedimiento verificado 2026-09-25. Cubre primera instalación y las
divergencias Windows/V2 encontradas (con sus fixes en el repo).

## Requisitos

- Python 3.12 + PyYAML: `python -m pip install pyyaml requests fastmcp`
  (`requests`/`fastmcp` los usa el MCP `foundry-vision`).
- Node.js (provee `npx`, usado por el MCP `playwright`).
- OpenCode V2 (verificar con `opencode --version`).

## Instalación

```powershell
$env:PYTHONUTF8 = 1   # obligatorio: sin esto render.py falla con cp1252
python adapters/shared/render.py
powershell -ExecutionPolicy Bypass -File tooling/sync.ps1 -Yes
```

`sync.ps1` regenera `adapters/opencode/out`, hace backup ZIP, copia
agentes/skills/plugin y fusiona solo `default_agent` en `opencode.json`
(MCPs y proveedores intactos). Tras cada sync, `opencode.json` puede quedar
con BOM (Set-Content); normalizar a UTF-8 sin BOM.

Reiniciar el servicio para cargar cambios: `opencode service restart`
(¡cierra la sesión actual!).

## `opencode.json` (formato V2)

Claves: `$schema`, `default_agent: master-orchestrator`, `mcp.servers`
(NO `mcp` plano, NO `env`, NO `enabled`):

| MCP | Tipo | Comando (ruta absoluta obligatoria en Windows) |
|-----|------|-----------------------------------------------|
| `playwright` | local | `npx.cmd` + `@playwright/mcp@latest` (`npx` sin extensión no spawnea) |
| `context7` | remote | `https://mcp.context7.com/mcp` |
| `github` | remote | `https://api.githubcopilot.com/mcp/` + OAuth (`/mcps` en el TUI) |
| `foundry-jev` | local | `python.exe` + `plugins/opencode/jev-mcp/server.py` (solo stdlib) |
| `foundry-vision` | local | `python.exe` + `adapters/lmstudio/vision_server.py` |
| `aws-mcp` | local, `disabled: true` | `uvx mcp-proxy-for-aws… --profile merkee` (activar tras `aws login`) |

Variables con `{env:NOMBRE}` llegan como **cadena vacía** si no están
definidas (no como ausentes). Los scripts deben tolerarlo (ver fixes).

## Fixes incluidos en este cambio

1. `adapters/lmstudio/vision_server.py`: `VLM_TIMEOUT_S`/`VLM_BASE_URL`
   vacíos crasheaban el arranque (`int("")`). Ahora `or` con defaults.
2. `adapters/shared/render.py::parity_report`: `read_text()` sin encoding
   rompía el build con locale cp1252. Ahora `encoding="utf-8"`.
3. `plugins/opencode/model-router/model-router.ts.tmpl`: port V1→V2
   (`export default { id, setup }`, hook `ctx.tool.hook("execute.before")`
   sobre tool `subagent`; sin imports — `@opencode/plugin` no resuelve
   desde `~/.config/opencode/plugins/`). Sin `chat.message`: V2 ya aplica
   el `model:` del agent file nativamente.

## Verificación

```powershell
powershell -ExecutionPolicy Bypass -Command "opencode mcp list"
# ✓ context7, foundry-jev, foundry-vision, playwright | ○ aws-mcp disabled
# ⚠ github needs authentication (OAuth manual, una vez)
Select-String -Path "$env:USERPROFILE\.local\share\opencode\log\opencode.log" `
  -Pattern "failed to load plugin" | Select-Object -Last 2  # vacío = OK
$env:PYTHONUTF8 = 1; python tooling/audit_matrix.py   # baseline: 10 hallazgos
python tooling/check_constraints.py                   # OK
```

## Pendiente del usuario (no automatizable)

- GitHub: `/mcps` → autenticar (OAuth, un splash).
- Jev dinámico: definir `AI_GATEWAY_API_KEY` (Vercel) o `JEV_API_KEY`.
- Visión local: LM Studio con `qwen3-vl-8b` + `VLM_MODEL` apuntando a su ID.
- AWS: instalar `aws-cli` + `uv`, `aws login --profile merkee`, quitar
  `disabled` de `aws-mcp` y reiniciar el servicio.
- ChatGPT OAuth: `/connect` en OpenCode (Luna/Terra/Sol para harness).
