---
name: openapi-first
description: Flujo API Design First para mantener specs, OpenAPI, implementación, clientes, tests y copias runtime sincronizados antes de escribir código.
---

# OpenAPI First Design

Este flujo prioriza el diseño del contrato de API antes de implementación. Define el proceso contract-first; los detalles de formato, error schema y convenciones OpenAPI viven en `openapi-standard`.

## Directrices de Diseño
- **Fuente de Verdad**: La ruta OpenAPI canónica del proyecto debe estar declarada en la spec/shared context y verificada leyendo el archivo real. Rutas comunes: `docs/api/openapi.yaml`, `docs/api/openapi.yml`, `src/main/resources/openapi.yaml`, `src/main/resources/openapi.yml` u otra ruta explícita definida por el proyecto.
- **Ownership**: Planner es el dueño de editar OpenAPI. Executor, Reviewer, Test Architect y otros agentes pueden leer OpenAPI, pero si detectan drift deben detenerse y reportarlo.
- Cualquier cambio en interfaz visible al cliente debe realizarse primero en el archivo OpenAPI canónico.
- No se permite implementar ni descomponer tareas de endpoints si OpenAPI está en drift frente a la spec validada.
- Todos los códigos de error, headers, request/response schemas, security requirements y side effects visibles al cliente deben estar en OpenAPI antes de implementación.
- Un drift OpenAPI/spec es blocker, no deuda técnica post-incremento.
- Si una skill de errores REST está activa, OpenAPI debe documentar el mismo schema de error que la spec. La estructura exacta se define en `openapi-standard` y/o la skill de error response del stack activo.
- Si el flujo transaccional visible al cliente difiere entre spec y OpenAPI, por ejemplo DB-first versus identity-provider-first, detener con `Blocked: OpenAPI/spec transaction drift`.
- El contrato debe declarar explícitamente auth/security, idempotency headers cuando apliquen, pagination, sorting/filtering, error responses, validation constraints y side effects visibles.

## Implementación
- **Controladores**: Los controladores web en `infrastructure` deben implementar las interfaces generadas por OpenAPI.
- **Segregación de Modelos**: Los DTOs definidos en el contrato son exclusivos para la comunicación externa. No deben utilizarse como entidades de dominio ni de persistencia.
- **Validación**: Las anotaciones de validación (Bean Validation) generadas a partir del contrato deben respetarse rigurosamente.
- **Gate**: Si el OpenAPI canonico no existe, no valida, o contradice la spec activa, detener y devolver `Blocked: OpenAPI contract not ready`.
- **Gate de evidencia**: Antes de aprobar descomposición, registrar endpoints, schemas y respuestas verificadas desde el archivo OpenAPI real, no desde un resumen de chat.

## Generación y Sincronización
- Si el proyecto usa generación de código, el generador debe configurarse según el stack activo y registrarse en la spec/shared context.
- Para Spring Boot con OpenAPI Generator, `interfaceOnly: true` es preferible cuando el proyecto genera interfaces de controllers y modelos DTO.
- Para frontend/clientes, los clientes generados deben derivarse del OpenAPI canónico, no de tipos escritos manualmente.
- Si existe una copia runtime del contrato, por ejemplo `src/main/resources/openapi.yaml`, Executor debe sincronizarla desde la fuente de diseño canónica antes de implementar o cerrar task board.
- El shared context debe distinguir fuente de diseño canónica y copias runtime/generadas.
- Las copias generadas o runtime no deben convertirse silenciosamente en fuente de verdad salvo decisión explícita de Planner.

## Gates de Validación
- Spec Validator debe bloquear si OpenAPI falta, no parsea, está incompleto o contradice spec/shared context.
- Task Decomposer no debe crear tareas ejecutables para endpoints sin contrato OpenAPI listo.
- Executor no debe editar OpenAPI; si implementación revela mismatch, debe detenerse con `Blocked: OpenAPI change requires Planner`.
- Reviewer debe marcar como `blocker` cualquier implementación que no siga el contrato.
- Test Architect debe cubrir status codes, schemas, validation, auth, error shape e idempotency definidos en OpenAPI.

## Evidencia Esperada
- Ruta absoluta del OpenAPI canónico.
- Endpoints revisados: method + path.
- Schemas revisados: request, response y error.
- Security requirements revisados.
- Runtime/generated copies sincronizadas o marcadas `not applicable`.
- Comando de validación/generación ejecutado si existe, o `skipped-with-reason`.
