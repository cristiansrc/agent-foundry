# ADR-0002: MCP local de solo lectura, alcance por proyecto y secreto vía Secret Service

- **Estado:** Accepted (fase de observación; implementación local pendiente de
  integración en la parte de launcher/SQLite)
- **Fecha de registro:** 2026-11-01
- **Ámbito:** `tooling/opencode_mcp.py`, `tooling/opencode_bridge.py`,
  `tooling/opencode_mcp_launch.py`, integración con ChatGPT Desktop.
- **Fuentes:** `docs/runbooks/chatgpt-opencode-phase2.md:3-40,42-70,119-154`;
  `docs/runbooks/chatgpt-opencode-phase1.md:46-55`;
  `tooling/opencode_mcp.py:1-32`;
  `tooling/opencode_bridge.py:1-5,20-117,256-374`;
  `tooling/opencode_mcp_launch.py:1-16,28-38,77-98,118-132`.

## Contexto

La observación desde Desktop necesita acceso a metadatos de sesiones y eventos
sin abrir una superficie de escritura ni duplicar la API de OpenCode. El host
puede tener varios proyectos; una selección global implícita mezclaría datos.
La API local puede exigir Basic auth, y el secreto no debe quedar en argumentos,
URL, repositorio ni configuración del cliente. La ventana de `GET /session` en
OpenCode 1.18.31 puede ser incompleta, y un vacío no debe interpretarse como
ausencia de actividad.

## Decisión

1. **Transporte:** MCP stdio local; la raíz se fija con `--projects-root` y cada
   consulta indica `project`. No hay selección global persistente.
2. **Solo lectura:** el servidor usa `GET` contra OpenCode y lectura del
   registro local/SQLite. No crea sesiones, no responde permisos, no escribe
   proyectos y no ejecuta agentes.
3. **Cinco herramientas:** `list_projects`, `list_sessions`,
   `get_session_status`, `get_session_events`, `get_session_messages`.
4. **Alcance por proyecto:** solo hijos directos reales con `.opencode/` o
   `install-manifest.yaml`; sin symlinks ni rutas anidadas; `same_project()`
   exige ruta real exacta. Las sesiones ajenas se descartan.
5. **Secreto:** el MCP nunca recibe la contraseña por argumentos, URL,
   repositorio ni configuración. `opencode_mcp_launch.py` la obtiene de Secret
   Service con `secret-tool` y la pasa solo en el entorno del `execve`.
   `DBUS_SESSION_BUS_ADDRESS` y `XDG_RUNTIME_DIR` deben estar disponibles en el
   proceso del cliente; no contienen el secreto.
6. **Integridad de la ventana:** `list_sessions` devuelve
   `{sessions, complete, source, note?}`. `complete=false` es parcial; un vacío
   incompleto no es concluyente.
7. **Respaldo:** si la API falla o la ventana es incompleta y vacía, se puede
   leer el historial SQLite en modo estricto (`mode=ro` +
   `PRAGMA query_only=ON`), solo columnas de metadatos, con `source=local` y
   límites. El esquema es un contrato externo; si no coincide, falla cerrado.
8. **Compatibilidad:** no se asume la API v2 ni parámetros no documentados. La
   referencia verificada es OpenCode 1.18.31; se comprueba `/doc` antes de usar
   información sensible.

## Consecuencias

- El cliente Desktop no puede ejecutar ni aprobar por este canal.
- La observación es bajo demanda; no hay stream en vivo ni push.
- La ausencia de eventos no prueba ausencia de acción; los informes deben
  declarar cobertura y límites.
- Un proyecto debe tener marca de Foundry/OpenCode para ser descubierto; no se
  sigue un symlink para “hacerlo aparecer”.
- El launcher no reenvía `--opencode-db`; con launcher, el respaldo SQLite solo
  autodetecta la ruta por defecto. Una ruta explícita requiere el servidor
  directo en desarrollo.
- Cambiar a escritura, a respuesta de permisos, a ejecución remota o a selección
  global de proyecto exige un ADR nuevo y una decisión de arquitectura/
  seguridad.

## Estado de implementación

- **Fase 2 (MCP base multiproyecto, cinco herramientas):** implementada en
  `a865eb0`, con tests en `tooling/tests/`.
- **Launcher Secret Service/D-Bus:** implementado localmente en
  `tooling/opencode_mcp_launch.py` (sin trackear) y su test; pendiente de
  integración/revisión. No se ejecutaron tests en la tarea documental.
- **Respaldo SQLite/`complete`/`source`:** implementado localmente en el diff de
  `opencode_bridge.py`, `opencode_mcp.py` y sus tests; pendiente de
  integración/revisión. No se inspeccionó el `.db` real.
- **Conexión real desde ChatGPT Desktop/Codex CLI:** no acreditada en el
  repositorio.

## No cubierto

Este ADR no decide el contrato de telemetría v2, el control plane, la
delegación controlada ni la ejecución remota. Son propuestas en
`docs/architecture.md` §5–§7.
