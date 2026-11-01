# Fase 1.5: prueba local ChatGPT–OpenCode

Fecha: 2026-11-01 UTC. Alcance: Agent Foundry y un proyecto temporal creado para esta prueba. No se instalaron componentes en proyectos corporativos ni se cambió la política de permisos.

## Resultado

- Fase 1 verificada: 48 pruebas unitarias, `tooling/lint.sh`, auditoría de matriz (0 hallazgos) y `tooling/build.sh` pasaron.
- El instalador aplicó el bundle OpenCode al proyecto temporal: 112 archivos, `master-orchestrator` como agente principal, observer y Permission Guardian incluidos. La configuración no añadió permisos automáticos. El comando `opencode run` se usó sin `--auto`.
- OpenCode 1.18.31 inició una API con contraseña en `127.0.0.1:4096`. El acceso anónimo a `/global/health` y `/doc` devolvió 401; con autenticación, `/global/health` devolvió versión 1.18.31 y `/doc` expuso OpenAPI 3.1 con rutas de sesiones y mensajes. El socket de esta prueba escuchó solo en loopback y se cerró al terminar.
- `tooling/opencode_bridge.py sessions` devolvió inicialmente `[]`. La prueba breve con `master-orchestrator` creó la sesión `ses_e6b757550ffeM95sYsiJrCKe48`; el puente leyó un mensaje de usuario con agente `master-orchestrator` y sin herramientas. `events` y `observe.py` registraron `session.error` y `session.idle`. El archivo de eventos se creó con modo 0600. Es evidencia de conexión a la API local y del observer, pero no de ejecución satisfactoria del modelo.
- La simulación clasificó una lectura interna como `read-candidate` y una escritura como `escalate-to-human`. En ambos casos devolvió `mode: simulation` y `requires_real_approval: true`. El Permission Guardian del plugin conserva sus controles de herramientas externas y subagentes; no responde solicitudes de permiso.

## Bloqueos y límites

- Las cuatro skills nuevas no pudieron copiarse a `~/.codex/skills` porque esa ruta respondió `Read-only file system`, aun después de concederse permiso de escritura en el sandbox. Las tres skills ya presentes coincidían con las salidas generadas. Las cuatro nuevas siguen preparadas en `adapters/chatgpt/out/skills/`.
- El lanzador habitual de `opencode` intentó instalar 2.1.2 con `mise` y falló por sistema de solo lectura. El binario 2.1.2 existente también intentó escribir un log en una ruta de solo lectura; con datos temporales arrancó, pero devolvió HTML en `/global/health`, `/doc` y `/session`, incompatible con el contrato esperado por el puente. La prueba de API usó el binario 1.18.31 ya instalado.
- La prueba de generación no produjo respuesta: el log de OpenCode informó `ProviderModelNotFoundError` para `openai/gpt-6-luna`; `/provider` solo informó `opencode` como proveedor conectado. No se cambiaron bindings de modelos ni credenciales.
- `ss` mostró otro listener preexistente en `100.119.146.13:4096`, independiente del servidor de prueba en loopback. No se identificó ni modificó ese proceso. La prueba no acredita el estado de exposición de ese otro listener.
- No se verificó ninguna conexión directa entre OpenCode y la conversación de ChatGPT referenciada. Solo se verificó la consulta local del puente desde este entorno.

## Siguientes pasos

1. En un entorno personal escribible, ejecutar `./tooling/build.sh` y `./tooling/sync-chatgpt.sh`, y comprobar que Codex descubra las cuatro skills nuevas. No modificar las tres skills existentes si siguen idénticas.
2. Resolver la discrepancia de CLI/API y confirmar `/doc`, autenticación y bind de loopback en la versión que vaya a usarse. Investigar por separado el listener preexistente de `100.119.146.13:4096` antes de usar el puerto como garantía de aislamiento.
3. Conectar un proveedor que ofrezca el modelo configurado para `master-orchestrator`, o evaluar y aprobar un cambio de binding mediante el flujo de modelos. Repetir una tarea mínima en un proyecto de prueba y verificar una respuesta, sesiones y eventos, manteniendo `--auto` deshabilitado.
