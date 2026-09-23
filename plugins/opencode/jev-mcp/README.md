# MCP `foundry-jev`

Servidor MCP local para consultar Jev como selector de agente, nivel de
razonamiento y necesidad de aclaración humana.

## Proveedor inicial

Vercel AI Gateway:

```bash
export FOUNDRY_JEV_PROVIDER=vercel
export AI_GATEWAY_API_KEY=...
```

El modelo usado es `typesafe-ai/jev` mediante `POST /v1/evaluate`.

## Proveedor alternativo

```bash
export FOUNDRY_JEV_PROVIDER=typesafe
export JEV_API_KEY=...
```

El modelo alternativo es `jev-latest` mediante la API oficial de Jev.

## Configuración OpenCode

La entrada local es equivalente a:

```json
{
  "mcp": {
    "foundry-jev": {
      "type": "local",
      "command": ["python3", "/ruta/absoluta/agent-foundry/plugins/opencode/jev-mcp/server.py"],
      "enabled": true
    }
  }
}
```

La credencial debe existir solo en el entorno del proceso. El servidor no
devuelve claves ni concede permisos: la matriz, los gates y el plugin siguen
siendo autoritativos.
