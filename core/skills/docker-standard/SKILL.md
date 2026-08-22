# Skill: Docker & Deployment Standard (IDIOMA: ESPAÑOL)

Este skill define cómo empaquetar y desplegar aplicaciones de forma segura y optimizada.

## Dockerfiles (Multi-stage)
1. **Build Stage**: Usar una imagen base completa para compilar (ej. `maven`, `node`, `python:3.12-slim`).
2. **Run Stage**: Usar una imagen mínima (Distroless o Alpine) para ejecutar.
3. **No Root**: Queda prohibido ejecutar el contenedor como root. Definir un usuario `appuser` sin privilegios.

## Docker Compose
- Debe existir un `docker-compose.yml` en la raíz para levantar dependencias locales (Base de datos, Redis, colas).
- Usar redes internas aisladas y nombres de contenedores descriptivos.

## Comportamiento del Agente
- El Executor debe asegurar que el `.dockerignore` esté presente y configurado para ignorar `node_modules`, `target`, `venv` y secretos.
- Los secretos de entorno deben pasarse mediante variables (`.env`) y nunca hardcodearse en el Dockerfile.
