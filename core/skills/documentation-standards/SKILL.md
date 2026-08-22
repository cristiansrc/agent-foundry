---
name: documentation-standards
description: Estándares de documentación técnica y READMEs.
---

# Estándares de Documentación

Define los requisitos mínimos y formatos permitidos para la documentación técnica dentro del ecosistema de servicios.

## Componentes de Documentación

### Diagramas Mermaid
- Uso obligatorio de Mermaid.js para diagramas de arquitectura, secuencia y estados.
- Los diagramas deben estar integrados directamente en los archivos Markdown.
- Mantener los diagramas actualizados con los cambios estructurales.

### Documentación de APIs
- Especificación obligatoria mediante Swagger/OpenAPI (v3+).
- Descripción detallada de cada endpoint, parámetros y esquemas de respuesta.
- Inclusión de ejemplos de peticiones y respuestas exitosas/fallidas.

### Guías de Instalación
- Pasos claros y secuenciales para configurar el entorno de desarrollo local.
- Listado de prerrequisitos (versiones de lenguajes, herramientas, bases de datos).
- Comandos de inicialización, ejecución de tests y construcción.

### Variables de Entorno
- Documentación de todas las variables necesarias en archivos `.env.example`.
- Descripción del propósito de cada variable y sus posibles valores.
- Clasificación de variables por entorno (Desarrollo, Staging, Producción).

### Registros de Decisiones de Arquitectura (ADRs)
- Obligatoriedad de registrar cualquier decisión técnica o de diseño relevante en `docs/architecture/decisions/000X-titulo-descriptivo.md`.
- Usar la plantilla MADR (Markdown Architectural Decision Records):
  ```markdown
  # [ADR-0001] Título de la Decisión Arquitectónica

  * **Estatus:** [propuesto | aceptado | superado | rechazado]
  * **Fecha:** AAAA-MM-DD
  * **Decisor:** enterprise-architect / planner

  ## Contexto y Problema
  Descripción breve del problema o necesidad técnica que requirió la decisión.

  ## Opciones Consideradas
  1. Opción A (ej. RabbitMQ)
  2. Opción B (ej. Apache Kafka)

  ## Decisión Elegida
  **Opción B**, porque satisface la necesidad de persistencia de eventos y replayability.

  ## Consecuencias
  * **Positivas:** Escalabilidad, desacoplamiento.
  * **Negativas:** Mayor complejidad de infraestructura en desarrollo local.
  ```
