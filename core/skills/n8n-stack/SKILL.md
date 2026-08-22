# Skill: n8n Workflow Convention (IDIOMA: ESPAÑOL)

Este skill define las convenciones para el desarrollo y gestión de flujos en n8n (GitOps).

## Estructura de Archivos
- **Workflows**: `workflows/*.json` (Exportaciones de flujos).
- **Templates**: `templates/` (Workflows base reutilizables).
- **Config**: `config/environments.json` (Variables por entorno).

## Comportamiento Obligatorio
1.  **GitOps**: Todos los cambios en workflows deben exportarse como JSON y versionarse.
2.  **No Secrets**: Queda prohibido guardar credenciales en los archivos JSON. Usar exclusivamente variables de entorno o el gestor de credenciales de n8n.
3.  **Modularidad**: Preferir el uso del nodo "Execute Workflow" para desacoplar lógicas complejas.

## Detección del Stack
- Si el repositorio contiene una carpeta `workflows/` con archivos `.json` de n8n, este skill se considera **ACTIVO**.
