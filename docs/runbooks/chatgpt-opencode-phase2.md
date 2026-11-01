# Fase 2: MCP local de lectura ChatGPT–OpenCode

`tooling/opencode_mcp.py` sirve metadatos de varios proyectos por stdio. La
raíz se fija al arrancar con `--projects-root`; **cada consulta** indica el
nombre `project`. No conserva una selección global entre llamadas.

## Alcance de proyectos

`list_projects` descubre únicamente directorios hijos directos y reales de
la raíz que contienen `.opencode/` o `install-manifest.yaml`. Esas marcas
constituyen la autorización de descubrimiento dentro de la raíz elegida. No
lista carpetas sin marca, rutas anidadas ni enlaces simbólicos. Los nombres
de proyecto son segmentos simples, no rutas. La ruta real de una sesión debe
coincidir con el proyecto seleccionado; las sesiones ajenas se descartan.

## Herramientas

| Herramienta | Entrada | Salida |
|---|---|---|
| `list_projects` | ninguna | Nombres de hasta 100 proyectos elegibles |
| `list_sessions` | `project` | Hasta 100 IDs, IDs padre y tiempos de sesiones verificadas |
| `get_session_status` | `project`, `session_id` | Tipo `idle`, `busy`, `retry` o `null` si no hay estado publicado |
| `get_session_events` | `project`, `session_id`, `limit` opcional | Hasta 100 eventos del registro local para esa sesión |
| `get_session_messages` | `project`, `session_id`, `limit` opcional | Hasta 100 metadatos de mensajes |

El estado, los eventos y los mensajes exigen primero verificar el directorio
de la sesión mediante `GET /session/:id`. Los eventos proceden de
`<proyecto>/.opencode/.foundry/events.jsonl`; solo se devuelven campos de
metadatos permitidos. Su ausencia no demuestra que no ocurrió una acción.
No se devuelven títulos, texto, prompts, argumentos, resultados ni detalles
de reintentos. Los errores no incluyen rutas ni fragmentos de respuesta.

El servidor solo usa GET para OpenCode y lectura del registro local. No crea
sesiones, no responde permisos y no escribe en proyectos. El transporte
HTTP, la autenticación Basic en tiempo de ejecución, el rechazo de proxies y
redirecciones, y la comprobación de destino local siguen en
`tooling/opencode_bridge.py`. Su CLI acepta el mismo modelo multiproyecto:
`--projects-root /mnt/data/Shares/Projects --project <nombre>` autoriza el
nombre con las mismas reglas antes de cualquier GET; sin `--projects-root`,
`--project` sigue siendo una ruta local validada sin enlaces.

## Comando para ChatGPT Desktop

En **Settings → MCP servers → Add server**, elegir **STDIO**:

```text
command: python3
args: /mnt/data/Shares/Projects/agent-foundry/tooling/opencode_mcp.py --projects-root /mnt/data/Shares/Projects --base-url http://100.119.146.13:4096
```

Equivalente en `config.toml` del host Codex local:

```toml
[mcp_servers.agent_foundry_opencode]
command = "python3"
args = ["/mnt/data/Shares/Projects/agent-foundry/tooling/opencode_mcp.py", "--projects-root", "/mnt/data/Shares/Projects", "--base-url", "http://100.119.146.13:4096"]
env_vars = ["OPENCODE_SERVER_PASSWORD", "OPENCODE_SERVER_USERNAME"]
```

El proceso Desktop necesita `OPENCODE_SERVER_PASSWORD` en su entorno mediante
el mecanismo local de secretos. `OPENCODE_SERVER_USERNAME` es opcional y
por defecto `opencode`. No colocar el secreto en argumentos, URL, repositorio
ni configuración. El servidor valida que la dirección sea loopback o una IP
literal que el kernel enrute localmente por `lo`. En el host inspeccionado
el 2026-10-31, `100.119.146.13:4096` cumplía esta condición; comprobar la
ruta de nuevo en otro host. No cambiar el bind ni reiniciar OpenCode.

Tras registrar el servidor, consultar `list_projects`, después
`list_sessions` con `project: "agent-foundry"`, y luego un estado o evento
con el mismo `project` y un `session_id` devuelto. Una lista vacía por sí
sola no demuestra conexión autenticada.

## Verificación

```bash
python3 -m unittest tooling.tests.test_opencode_bridge tooling.tests.test_opencode_mcp
```

Las pruebas usan respuestas simuladas de OpenCode y un proceso MCP stdio
real con proyectos temporales. Prueban aislamiento entre proyectos, validación
de IDs, límites y rechazo de enlaces. No acreditan una conexión real desde
ChatGPT Desktop. Para acreditarla faltan un secreto heredado por Desktop,
una respuesta autenticada del OpenCode local y una llamada desde ese cliente.
No se ha cambiado la conectividad ni solicitado permisos para esta fase.

Fase 1 y evidencia histórica: `chatgpt-opencode-phase1.md` y
`chatgpt-opencode-phase15-results.md`.
