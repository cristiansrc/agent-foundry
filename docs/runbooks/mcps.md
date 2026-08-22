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

## Pendientes de decisión (no instalados)

### Visión para modelos sin visión (local, gratis)
Requiere Ollama + un VLM:
```bash
ollama pull qwen3-vl:8b     # ~6GB, mejor balance
```
Opciones de servidor (elegir UNO):
- **vision-sidecar-mcp** (xronocode): `analyze_ui_screenshot` con viewport hints,
  OCR endurecido, detección de clipping — hecho para agentes + Playwright.
- **mh-vision-mcp** (mohamedhusseinios): multi-provider (Ollama/OpenAI/Anthropic),
  tools: describe_image, extract_ui, ocr, analyze_diagram.

Útil para: hyprmind-vision-analyst (fallback local), ui-designer (revisar
artboards renderizados), cualquier agente texto-only que reciba screenshots.

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
