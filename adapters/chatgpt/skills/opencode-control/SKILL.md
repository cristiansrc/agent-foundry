---
name: opencode-control
description: Consulta sesiones y eventos de OpenCode desde ChatGPT Desktop mediante el puente local de Agent Foundry; úsala para observar un flujo sin ejecutarlo ni responder permisos.
---

# Control de OpenCode, fase de observación

Identifica el proyecto destino explícito. Si está conectado el MCP local de fase 2, usa `list_sessions`, `get_session_statuses`, `get_session_messages` y `get_session_events` para consultar solo metadatos de ese proyecto. Si no está conectado, ejecuta `python3 <foundry>/tooling/opencode_bridge.py --project <proyecto> sessions`, `... statuses`, `... session <id>` y `... events` según la consulta. Los mensajes y argumentos pueden contener datos sensibles y no deben copiarse a informes.

El puente usa `GET` en la API HTTP local de OpenCode. Configura `--base-url` si el puerto difiere. No uses endpoints `POST`, `PATCH` ni `DELETE` de OpenCode en esta fase. La conexión no inicia sesiones ni ejecuta `master-orchestrator`; este sigue siendo el agente principal del harness. Si falta el servidor o el observador, indica la fuente ausente sin inferir que no ocurrió actividad.

Para instalar y verificar el MCP, lee `docs/runbooks/chatgpt-opencode-phase2.md` de Agent Foundry. Para el puente previo, consulta `chatgpt-opencode-phase1.md`.
