# Runbook: Stack de Servidores MCP

Estrategia de MCPs por herramienta. Config activa en `~/.config/opencode/opencode.json`
(esta capa es infraestructura del tool, NO la genera agent-foundry; este doc
registra el qué y el por qué).

## Reglas

1. **Presupuesto de contexto**: cada MCP agrega tool definitions a cada request.
   Mantener 4-6 activos globales. Los especializados van per-proyecto o
   deshabilitados (`enabled: false`) hasta necesitarlos.
2. **Per-agent scoping**: un MCP puede dejarse globalmente apagado y encenderse
   solo para un agente vía `"agent": { "<nombre>": { "tools": { "mcp_*": true } } }`.
3. **Verificar mantenimiento** antes de instalar: varios servidores oficiales de
   referencia (puppeteer, postgres, slack) fueron archivados — usar sucesores.

## Stack global activo (opencode)

| MCP | Tipo | Sirve a | Notas |
|-----|------|---------|-------|
| `aws-mcp` | local (uvx proxy) | devops-architect, bug-diagnostician | FIX 2026-08-22: clave `env` → `environment` (la anterior se ignoraba silenciosamente) |
| `playwright` | local (npx @playwright/mcp) | functional-tester-agent, ui-designer (self-test visual) | Reemplaza puppeteer (ARCHIVADO). 23 tools default |
| `context7` | remote mcp.context7.com | executor, planner, architect-executor | Docs versionadas reales (Spring Boot, React 19...). Mata APIs alucinadas. Solo 2 tools |
| `github` | remote api.githubcopilot.com + OAuth | git-executor | PRs, issues, Actions. Primera vez: `opencode mcp auth github` |
| `foundry-jev` | local (stdio) | master-orchestrator y agentes con routing dinámico | Selecciona agente, nivel de razonamiento y aclaración humana. Proveedor inicial Vercel (`AI_GATEWAY_API_KEY`); alternativa Jev oficial (`JEV_API_KEY`). |

## Pendientes de decisión (no instalados)

### Visión: modelos con visión nativa (MCP local retirado)
**RETIRADO 2026-09-27**: el MCP propio `foundry-vision` (LM Studio) se eliminó
(`adapters/lmstudio/` borrado) por falta de uso. Todos los agentes que necesitan
ver imágenes usan modelos con visión nativa: `ui-designer` (Sol v6),
`ui-executor` y `functional-tester-agent` (DeepSeek Vision), `reviewer`
(MiMo v2.6). Si algún modelo sin visión necesitara ver capturas en el futuro,
revaluar un puente local antes de reintroducirlo.

### Por proyecto (activar cuando aplique)
- **Postgres MCP Pro** (Crystal DBA): EXPLAIN + índices hipotéticos, modo
  read-only. Para database-architect/bug-diagnostician contra DBs reales.
- **Sentry**: errores de producción en el loop de fix (OAuth).
- **Figma Dev Mode**: si el diseño llega desde Figma real (complementa
  ui-designer, no lo reemplaza).

### Descartados (con razón)
- `puppeteer`: archivado oficialmente → playwright.
- `sequential-thinking`: los modelos actuales ya razonan nativo; latencia sin payoff.
- `slack`/brave-search reference servers: archivados o rate-limit hostil.

## Verificación post-cambio

```bash
opencode mcp list          # estado y auth de cada server
```

Si un MCP remoto pide auth: `opencode mcp auth <nombre>`.
