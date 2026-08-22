---
name: api-governance-linter
description: Reglas de auditoría de contratos OpenAPI 3.0/3.1, detección de Breaking Changes y políticas de versión semántica (SemVer) para el agente api-governance-agent.
---

# API Governance & Breaking Changes Linter

Guía operativa para el agente `api-governance-agent` para garantizar que las evoluciones en los contratos de API no rompan la compatibilidad con clientes existentes.

---

## 1. Clasificación de Cambios en OpenAPI

### ❌ Breaking Changes (Cambios Incompatibles)
Cualquier cambio que requiera modificaciones en los clientes existentes para evitar fallos:
- Eliminar un endpoint (`path` o método HTTP).
- Renombrar un parámetro de consulta, cabecera o propiedad de JSON.
- Cambiar el tipo de dato de una propiedad existente (ej: `integer` ➔ `string`).
- Agregar un nuevo parámetro requerido (`required: true`) en el Request Body o Query.
- Eliminar o cambiar códigos de respuesta HTTP esperados (ej: cambiar 200 por 201 en un endpoint existente).

### ✅ Non-Breaking Changes (Cambios Compatibles)
- Agregar un nuevo endpoint (`path` o método).
- Agregar una nueva propiedad opcional (`required: false`) en el Request Body o Query.
- Agregar nuevas respuestas de error 4xx/5xx bien documentadas.
- Marcar una propiedad o endpoint como obsoleto (`deprecated: true`).

---

## 2. Estrategia de Deprecación y Versionado Semántico (SemVer)

- **Versión MAJOR (v1 ➔ v2)**: Requerida cuando se introducen Breaking Changes inevitables. El nuevo path debe incluir el prefijo `/api/v2/...` manteniendo `/api/v1/...` operativo durante el período de migración.
- **Header de Deprecación**: Los endpoints obsoletos deben incluir las cabeceras HTTP:
  ```http
  Deprecation: true
  Sunset: Wed, 11 Nov 2026 00:00:00 GMT
  ```

---

## 3. Checklist de Auditoría para `api-governance-agent`

1. ¿El contrato OpenAPI define respuestas estructuradas de error REST siguiendo el estándar del stack (`springboot-java`, `fastapi`, etc.)?
2. ¿Todos los endpoints tienen `operationId`, `summary` y etiquetas (`tags`) adecuadas?
3. ¿Existen diferencias destructivas en las propiedades JSON entre la spec del incremento y la Master Spec?
4. ¿Los endpoints paginados incluyen parámetros de `page`, `size` y respuesta envelopada?
