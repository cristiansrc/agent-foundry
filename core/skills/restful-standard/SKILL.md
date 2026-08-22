---
name: restful-standard
description: Convenciones REST para recursos, metodos HTTP, status codes, paginacion, filtros, versionado, compatibilidad, seguridad e idempotencia.
---

# RESTful Standard

Esta skill define semantica REST y convenciones de API HTTP. La forma exacta del contrato OpenAPI vive en `openapi-standard`; la estructura de errores vive en la skill de error response del stack activo o en el estandar de error definido por el proyecto.

## Recursos y URLs
- Modelar rutas como recursos, no acciones CRUD: usar `/users`, no `/getUsers`.
- Usar plural para colecciones: `/orders`, `/payment-methods`.
- Usar `kebab-case` para paths y segmentos de URL.
- Usar nesting solo cuando exprese pertenencia real y estable: `/customers/{customer_id}/addresses`.
- Evitar nesting profundo; mas de dos niveles suele indicar que falta un recurso propio o un filtro.
- Usar IDs publicos estables en URLs, preferiblemente UUIDs cuando aplique.
- No exponer IDs internos secuenciales, nombres de tablas, claves compuestas internas ni detalles de infraestructura si el recurso es publico.
- Mantener nombres consistentes entre URL, OpenAPI schema y lenguaje ubicuo del dominio.

## Metodos HTTP
- `GET`: consultar recursos; debe ser seguro e idempotente; no debe cambiar estado.
- `POST`: crear recursos o ejecutar comandos no idempotentes cuando no exista una mejor representacion de recurso.
- `PUT`: reemplazar completamente un recurso identificado; debe ser idempotente.
- `PATCH`: modificar parcialmente un recurso; documentar semantica del patch usado.
- `DELETE`: eliminar o desactivar un recurso; debe ser idempotente desde la perspectiva del cliente.
- No usar `GET` para operaciones con side effects.
- No usar verbos en rutas cuando el metodo HTTP ya expresa la accion.
- Para acciones de negocio que no encajan en CRUD, modelar un subrecurso o comando explicito: `/orders/{order_id}/cancellations`, `/password-reset-requests`.

## Status Codes
- `200 OK`: lectura exitosa o operacion con body de respuesta.
- `201 Created`: recurso creado; incluir `Location` cuando exista URL publica del recurso.
- `202 Accepted`: procesamiento asincrono aceptado; incluir forma de consultar estado si aplica.
- `204 No Content`: exito sin body, comun en `DELETE` o actualizaciones sin respuesta.
- `400 Bad Request`: request mal formado, tipos invalidos o validacion sintactica.
- `401 Unauthorized`: autenticacion ausente, invalida o expirada.
- `403 Forbidden`: usuario autenticado sin permisos.
- `404 Not Found`: recurso inexistente o no visible para el cliente.
- `409 Conflict`: conflicto de estado, duplicado, version o concurrencia.
- `422 Unprocessable Entity`: regla de negocio invalida con request sintacticamente correcto.
- `429 Too Many Requests`: rate limit.
- `500 Internal Server Error`: error inesperado.
- `503 Service Unavailable`: dependencia o servicio temporalmente no disponible.
- No retornar `200` para errores funcionales.
- No ocultar errores de validacion como respuestas exitosas con flags tipo `success: false`.

## JSON y Naming
- La convencion de atributos JSON debe ser unica por API. Si no hay decision explicita, usar `snake_case` para APIs nuevas.
- No mezclar `camelCase` y `snake_case` dentro del mismo contrato salvo integracion legacy documentada.
- Usar nombres de campos orientados al negocio, no a implementacion interna.
- Usar `*_at` para instantes (`created_at`) y `*_date` para fechas de calendario cuando el proyecto use `snake_case`.
- Usar enum values estables en `UPPER_SNAKE_CASE`, salvo convencion existente distinta.
- No exponer campos internos como `deleted`, `version`, `tenant_internal_id` o flags tecnicos si no son parte del contrato publico.

## Paginacion, Filtros y Ordenamiento
- Usar `page` y `size` para paginacion basada en pagina cuando el dominio no requiera cursor.
- Definir si `page` inicia en `0` o `1`; no asumirlo implicitamente.
- Documentar `size` default y maximo.
- Usar `sort` con formato estable, por ejemplo `sort=created_at,desc`.
- Los filtros simples pueden ser query params directos: `status=ACTIVE`.
- Para filtros complejos, documentar una convencion unica; no inventar sintaxis distinta por endpoint.
- Respuestas paginadas deben incluir lista de items y metadata suficiente: pagina actual, size, total cuando sea viable, o cursor/next token si es paginacion por cursor.
- No retornar colecciones potencialmente grandes sin paginacion o limite explicito.

## Versionado y Compatibilidad
- Preferir versionado por path (`/v1`) o por header solo si el ecosistema ya lo soporta; no mezclar estrategias en la misma API.
- Cambios compatibles: agregar campos opcionales, agregar endpoints, agregar enum values solo si clientes estan preparados.
- Cambios incompatibles: renombrar campos, cambiar tipos, eliminar campos, cambiar semantica de status codes, volver required un campo opcional.
- No romper contratos publicos sin version nueva o proceso de deprecacion documentado.
- Campos deprecated deben marcarse en OpenAPI y conservar comportamiento durante la ventana acordada.
- La compatibilidad debe validarse contra OpenAPI, tests y clientes generados cuando existan.

## Idempotencia y Concurrencia
- Operaciones de creacion o comandos sensibles a reintentos deben soportar `Idempotency-Key` cuando el cliente pueda repetir requests por timeout o retry.
- Documentar el scope y duracion de `Idempotency-Key` si se usa.
- Actualizaciones concurrentes deben usar una estrategia explicita: ETag/`If-Match`, version de recurso o bloqueo de negocio.
- Si una operacion no es idempotente, documentar el riesgo y evitar retries automaticos no controlados.
- No implementar retries de cliente sobre `POST` no idempotente sin clave de idempotencia.

## Seguridad HTTP
- Exigir HTTPS fuera de entornos locales.
- Validar `Content-Type` y `Accept` cuando el endpoint use payloads negociables.
- Documentar autenticacion y autorizacion en OpenAPI; no dejar endpoints protegidos sin `security`.
- No filtrar si un recurso existe cuando la politica de seguridad exige ocultarlo; en ese caso `404` puede ser correcto.
- No exponer tokens, secretos, PII innecesaria ni detalles internos en respuestas o errores.
- Aplicar rate limiting en endpoints sensibles o publicos.

## Errores
- Los errores deben usar la estructura estandar del proyecto y estar documentados en OpenAPI.
- No devolver strings sueltos, mapas ad hoc o HTML para APIs JSON.
- No exponer stack traces ni mensajes internos.
- Diferenciar validacion sintactica (`400`) de regla de negocio (`422`) cuando el proyecto adopte esa separacion.
- Usar `409` para conflictos recuperables por el cliente, no `500`.
- Cada error funcional relevante debe tener codigo estable apto para frontend/i18n.

## OpenAPI y Evidencia
- Cada endpoint REST debe estar documentado en el OpenAPI canonico antes de implementarse.
- OpenAPI debe reflejar metodo, path, params, request body, responses, security, paginacion, filtros e idempotencia.
- Si la implementacion difiere de OpenAPI, detener con `Blocked: REST/OpenAPI drift`.
- Evidencia esperada: endpoints revisados, status codes, estrategia de paginacion/filtros, versionado, seguridad y errores.
