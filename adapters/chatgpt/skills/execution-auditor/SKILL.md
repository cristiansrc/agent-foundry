---
name: execution-auditor
description: Audita la ejecución de agentes OpenCode con metadatos de sesiones y eventos de Agent Foundry; úsala para detectar lagunas de observabilidad y contrastar evidencias sin leer contenido sensible por defecto.
---

# Auditoría de ejecución

Obtén sesiones con `opencode-control` y eventos con `python3 <foundry>/tooling/opencode_bridge.py --project <proyecto> events`. Correlaciona por `session_id`, orden temporal y `call_id` cuando exista. Contrasta con el recibo `.opencode/foundry-install.json`, la versión del bundle y los artefactos canónicos del incremento si el usuario los proporcionó.

Separa lo observado de lo inferido. La ausencia de un evento no prueba que un paso no se ejecutó; el observador puede fallar sin detener OpenCode. Los metadatos tampoco prueban calidad, cumplimiento de spec, coste, ni autenticidad de aprobaciones G1/G2. Señala estas brechas y propón pruebas o eventos adicionales antes de recomendar cambios de agente.

No publiques IDs de sesión, rutas de proyectos, títulos, prompts, argumentos, respuestas o secretos en informes compartibles. Usa ejemplos sintéticos.
