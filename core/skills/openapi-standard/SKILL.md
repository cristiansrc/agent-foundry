---
name: openapi-standard
description: Convenciones concretas para escribir contratos OpenAPI: version, estructura, schemas, parametros, seguridad, errores, ejemplos y validacion.
---

# OpenAPI Standard

Esta skill define convenciones de formato para contratos OpenAPI. El flujo contract-first vive en `openapi-first`; la semantica REST vive en `restful-standard`; la implementacion de errores por stack vive en skills como `springboot-java-rest-error-response-standards`, `springboot-kotlin-rest-error-response-standards` o `fastapi-rest-error-response-standards`.

## Version y Formato
- Usar OpenAPI `3.1.x` o `3.2.x` si el tooling del proyecto lo soporta. Si el generador, validador o framework solo soporta `3.0.x`, documentar la restriccion en shared context.
- No declarar versiones inexistentes o experimentales como `4.0`.
- Preferir YAML para contratos fuente humanos; JSON es aceptable para artefactos generados.
- El contrato debe parsear sin errores antes de generar codigo, implementar endpoints o crear clientes.
- El campo `info.version` describe la version del contrato/API, no la version de OpenAPI.
- Definir `servers` por ambiente solo si las URLs son estables y no exponen datos internos.

## Estructura Obligatoria
- Todo endpoint debe tener `operationId` unico, estable y orientado a accion de negocio, por ejemplo `createUser`, `findOrderById`.
- Todo endpoint debe tener `tags`, `summary`, `description` cuando la semantica no sea obvia, parametros, request body si aplica y respuestas esperadas.
- Reutilizar `components.schemas`, `components.parameters`, `components.responses`, `components.headers` y `components.securitySchemes`; no duplicar estructuras inline salvo casos triviales.
- Los schemas publicos deben representar DTOs de contrato, no entidades de dominio ni tablas.
- Los nombres de schemas deben ser estables y expresivos: `CreateUserRequest`, `UserResponse`, `PagedOrderResponse`, `ApiErrorResponse`.
- Evitar schemas ambiguos como `Object`, `Data`, `Response`, `Payload` o `MapStringObject` salvo que el contrato realmente sea abierto.

## Naming y JSON
- Las rutas siguen `restful-standard`: recursos en plural, `kebab-case` y sin verbos CRUD en el path.
- Los atributos JSON deben seguir la convencion del proyecto. Si no hay decision explicita, usar `snake_case` para APIs nuevas por compatibilidad con `restful-standard`.
- No mezclar `camelCase` y `snake_case` en el mismo contrato salvo integracion legacy documentada.
- Los enum values deben ser strings estables en `UPPER_SNAKE_CASE`, salvo convencion distinta ya existente.
- Fechas e instantes deben usar `type: string` con `format: date` o `format: date-time`; `date-time` debe serializarse en UTC cuando represente un instante.
- Identificadores publicos deben modelarse como `string`, preferiblemente `format: uuid` cuando aplique.

## Requests, Responses y Status Codes
- Cada operacion debe declarar todos los status codes funcionalmente esperados, no solo `200` y `500`.
- `POST` de creacion debe declarar `201` y header `Location` cuando el recurso tenga URL publica.
- `DELETE` exitoso sin cuerpo debe declarar `204`.
- No usar `200` para errores funcionales.
- `requestBody.required` debe ser `true` cuando el endpoint no pueda operar sin body.
- Declarar `content` explicitamente; usar `application/json` para payloads JSON y `application/problem+json` o el media type de error definido por el proyecto para errores.
- Las respuestas paginadas deben declarar metadata de paginacion y lista de items con schema tipado.

## Parametros y Validaciones
- Todo `path parameter` debe estar marcado como `required: true` y tener schema.
- Query params de paginacion deben documentar default, minimo y maximo cuando aplique: `page`, `size`, `sort`.
- Query params de filtro deben declarar tipo, formato, valores permitidos y si combinan con otros filtros.
- Declarar restricciones en schemas: `required`, `minLength`, `maxLength`, `minimum`, `maximum`, `pattern`, `format`, `enum`, `nullable` o union con `null` segun version/tooling.
- No confiar en validaciones descritas solo en texto si OpenAPI puede expresarlas como schema.
- Ejemplos no reemplazan constraints; ambos deben coexistir cuando agreguen valor.

## Seguridad
- Definir `components.securitySchemes` para los mecanismos reales: bearer JWT, OAuth2/OIDC, API key, mTLS u otros.
- Cada operacion debe declarar `security` explicitamente si difiere del default global.
- No documentar endpoints protegidos como anonimos por omision.
- No incluir tokens, credenciales, dominios internos sensibles ni datos personales reales en examples.
- Si hay scopes/roles relevantes, documentarlos en OpenAPI o en una referencia de seguridad vinculada.

## Errores
- El contrato OpenAPI debe usar una sola estructura de error por API o bounded context.
- Para APIs Spring Boot Java que usen `springboot-java-rest-error-response-standards`, Spring Boot Kotlin que usen `springboot-kotlin-rest-error-response-standards`, o FastAPI que usen `fastapi-rest-error-response-standards`, documentar `ApiErrorResponse` y `ApiErrorDetail` con campos `timestamp`, `status`, `error`, `code`, `message`, `path`, `trace_id` y `details`.
- Si el proyecto adopta RFC 9457 Problem Details, usar `ProblemDetails` de forma consistente y no mezclarlo con `ApiErrorResponse` en el mismo contrato salvo adaptador documentado.
- Cada respuesta `4xx` y `5xx` debe referenciar el schema de error estandar mediante `$ref`.
- Cada endpoint debe declarar errores esperados de validacion, autenticacion, autorizacion, inexistencia, conflicto o regla de negocio cuando apliquen.
- Cualquier divergencia entre spec prose, OpenAPI, tests y handler runtime es blocker.

## Ejemplos
- Agregar examples representativos para request, success response y error response en endpoints publicos o complejos.
- Los examples deben ser validos contra el schema.
- No usar valores irreales que oculten reglas importantes, por ejemplo strings vacios en campos required.
- No incluir informacion sensible, tokens reales, correos personales reales ni IDs de produccion.

## Referencias y Modularizacion
- Usar `$ref` para componentes reutilizables.
- Mantener referencias relativas simples y resolubles desde el archivo canonico.
- No introducir referencias remotas externas sin justificacion, porque pueden romper generacion, validacion offline o seguridad.
- Si el contrato se divide en multiples archivos, registrar la entrada canonica y el comando de bundling/validation en shared context.

## Validacion Esperada
- Ejecutar el validador/linter/generador configurado por el proyecto si existe.
- Si no existe herramienta configurada, reportar `skipped-with-reason` y validar al menos parseo YAML/JSON y consistencia visual de endpoints, schemas y respuestas.
- Spec Validator debe bloquear contratos sin version valida, sin schemas de error consistentes, con operationIds duplicados, con endpoints sin security requerida o con status codes incompletos.
- Reviewer debe marcar como `blocker` cualquier implementacion que exponga un contrato distinto al OpenAPI canonico.

## Evidencia Esperada
- Version OpenAPI usada y razon si no es `3.1.x` o `3.2.x`.
- Ruta absoluta del contrato canonico.
- Comando de validacion/lint/generacion ejecutado o `skipped-with-reason`.
- Endpoints revisados con method + path.
- Schemas principales y schema de error revisados.
- Security schemes y operaciones anonimas verificadas.
