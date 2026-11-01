---
name: permission-guardian
description: Evalúa en simulación solicitudes de permisos de OpenCode para orientar revisión humana; úsala cuando se quiera clasificar una acción sin concederla ni modificar políticas reales.
---

# Permission Guardian, simulación

Prepara un JSON local con `action` y `resources` (rutas absolutas) y ejecuta `python3 <foundry>/tooling/opencode_bridge.py --project <proyecto> simulate --request <archivo>`. El resultado distingue candidatos de lectura interna y acciones que deben escalarse. `requires_real_approval` siempre es `true`.

La recomendación no llama la API de respuesta a permisos ni modifica `profiles/permissions.yaml`, reglas de OpenCode o firmas G1/G2. Evalúa el caso concreto y remite la solicitud real al usuario por el mecanismo nativo de OpenCode. Ante rutas relativas, externas, herramientas con efectos, datos insuficientes o incertidumbre, escala al humano.

No pegues argumentos de herramientas ni secretos en el JSON de simulación. Para la conexión, consulta `docs/runbooks/chatgpt-opencode-phase1.md`.
