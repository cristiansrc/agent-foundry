# Fase 1: observación ChatGPT–OpenCode

`master-orchestrator` sigue siendo el orquestador en OpenCode. ChatGPT Desktop
consulta metadatos y audita evidencias; no responde permisos, no ejecuta tareas
y no firma gates. Las cuatro skills de `adapters/chatgpt/skills/` son exclusivas
de ChatGPT Desktop. No se instalan en el bundle OpenCode.

## Conexión local

1. Construir el adapter: `./tooling/build.sh`. Revisar el diff generado.
2. Instalar las skills en ChatGPT Desktop con `CODEX_SKILLS_DIR=<directorio-de-prueba> ./tooling/sync-chatgpt.sh`; omitir la variable solo cuando se quiera instalarlas en el directorio personal de Codex. Esto no instala el harness.
3. En el proyecto destino, instalar el bundle OpenCode siguiendo `docs/runbooks/opencode-harness.md` y reiniciar OpenCode. El observador escribe `<proyecto>/.opencode/.foundry/events.jsonl` con permisos locales. No sincronizar ni publicar ese archivo.
4. Arrancar un servidor OpenCode en `127.0.0.1` con un puerto conocido, por ejemplo `opencode serve --hostname 127.0.0.1 --port 4096`. Configurar `OPENCODE_SERVER_PASSWORD` en el entorno antes de arrancarlo y en el cliente; no pasar la contraseña en URL ni en la línea de comandos. Verificar la versión y el contrato del servidor instalado en `/doc` antes de usarlo con información sensible.
5. Consultar desde la raíz de Foundry:

```bash
python3 tooling/opencode_bridge.py --project <proyecto> sessions
python3 tooling/opencode_bridge.py --project <proyecto> session <id> --limit 50
python3 tooling/opencode_bridge.py --project <proyecto> events --limit 100
python3 tooling/observe.py --project <proyecto>
```

El puente admite `--base-url http://127.0.0.1:<puerto>`. Solo acepta loopback,
usa `GET`, rechaza redirecciones y filtra sesiones por el directorio del
proyecto. Devuelve IDs, tiempos, agentes, nombres de herramientas y eventos;
no imprime títulos, prompts, argumentos, respuestas ni resultados. El resumen
de eventos es parcial si el plugin no estuvo instalado o falló.

## Simulación de permisos

Guardar un JSON local con datos sintéticos, por ejemplo
`{"action":"read","resources":["/ruta/absoluta/del/proyecto/archivo"]}` y ejecutar:

```bash
python3 tooling/opencode_bridge.py --project <proyecto> simulate --request <solicitud.json>
```

`read-candidate` significa una lectura interna candidata a revisión;
`escalate-to-human` significa acción con efectos, ruta externa o insuficiente.
Ambas respuestas mantienen `requires_real_approval: true`. La clasificación
no replica todas las reglas nativas de OpenCode y no autoriza ninguna acción.
El permiso real queda en la UI de OpenCode. Cambiar reglas de seguridad,
implementar respuestas automáticas o escribir un gateway con operaciones de
control exige una decisión y autorización posteriores.

## Arquitectura y límites

El gateway HTTP adicional o MCP no encaja en esta fase: la API local de OpenCode
ya ofrece lectura de sesiones y el observador del bundle aporta eventos.
Añadir otro servidor aumentaría la superficie de acceso y duplicaría contratos.
La API documentada por OpenCode incluye `/session`, `/session/:id/message` y
`/event`; este puente usa únicamente los dos primeros. El registro local permite
leer eventos sin abrir un stream de larga duración. Los eventos no contienen
resultado funcional, tokens ni costes por paso, por lo que una auditoría de
cumplimiento necesita contrastar artefactos y pruebas de cada incremento.

Referencia de API: https://docs.opencode.ai/docs/server/
