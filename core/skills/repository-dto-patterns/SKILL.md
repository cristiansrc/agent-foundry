---
name: repository-dto-patterns
description: Patrones para separar modelos de dominio, DTOs de transporte, entidades de persistencia, repositories/adapters y mappings entre capas.
---

# Repository and DTO Patterns

Esta skill define como separar modelos y accesos a datos entre capas. No define arquitectura completa; los boundaries generales viven en `hexagonal-architecture`. No define estilo de lenguaje; Java y Kotlin delegan a `java-stack` y `kotlin-stack`.

## Principio Central
- Ningun modelo tecnico debe cruzar boundaries incorrectos.
- El dominio no debe conocer DTOs de API, OpenAPI generated models, entidades JPA, documentos Mongo, rows SQL, ORM sessions, HTTP, JSON ni framework annotations.
- La aplicacion trabaja con modelos de dominio, commands, queries, results y output ports.
- Infraestructura adapta persistencia, transporte y clientes externos hacia los modelos de aplicacion/dominio.
- Cada conversion entre capas debe estar ubicada y justificada; los mappings invisibles o accidentales son fuente de bugs.

## Tipos de Modelos
- **Domain model**: entidades, value objects, domain events y reglas de negocio puras.
- **Application command/query/result**: modelos internos de caso de uso, independientes de HTTP y persistencia.
- **API DTO / contract model**: request/response externos, normalmente definidos por OpenAPI o por el framework API.
- **Persistence entity/document/row**: modelo tecnico de almacenamiento, como JPA Entity, Mongo document, SQL row model o ORM model.
- **Integration DTO**: payloads hacia/desde sistemas externos, colas, webhooks, n8n o clients.

Regla: no reutilizar un modelo tecnico como si fuera modelo de otra capa por conveniencia.

## Repositories y Output Ports
- Los output ports de persistencia viven en `application`, no en dominio puro, salvo que el proyecto tenga una convencion explicita distinta.
- Los output ports deben devolver modelos de dominio o results de aplicacion, no entidades JPA/documentos/rows.
- Las implementaciones tecnicas de repositories viven en `infrastructure` como driven adapters.
- En Spring Data JPA, las interfaces `JpaRepository` pertenecen a infraestructura y no deben exponerse a aplicacion/dominio.
- En FastAPI/SQLAlchemy o similares, sessions, ORM models y query builders pertenecen a infraestructura.
- No filtrar detalles de persistencia hacia use cases: `Pageable`, `EntityManager`, `Session`, `CriteriaBuilder`, `QuerySet` o equivalentes no deben cruzar el puerto salvo que exista un wrapper de aplicacion.
- Las consultas optimizadas o projections pueden existir en infraestructura, pero su salida debe mapearse a results/DTOs internos definidos por aplicacion.

## DTOs de API
- Los DTOs de API representan el contrato externo, no el dominio.
- Si el proyecto usa OpenAPI First, los DTOs generados pertenecen al adapter HTTP/infrastructure.
- Los DTOs de request deben validar formato de entrada en el borde; las reglas de negocio viven en dominio/aplicacion.
- Los DTOs de response deben exponer solo datos publicos del contrato, no campos internos de entidades.
- No pasar DTOs de API a use cases salvo como command/result de aplicacion explicitamente construido.
- No retornar entidades de dominio directamente como response HTTP si eso acopla el contrato publico al modelo interno.

## Entidades de Persistencia
- Las entidades/documentos/rows de persistencia pertenecen a infraestructura.
- No deben contener reglas de negocio centrales; solo reglas tecnicas de persistencia, constraints locales y conversiones simples si el stack lo permite.
- No exponer entidades de persistencia fuera del adapter.
- No usar entidades JPA como dominio en arquitectura hexagonal.
- Auditoria, soft delete, optimistic locking y detalles de indices pertenecen al modelo de persistencia y a la skill de datos correspondiente.
- Si una regla de negocio depende de un estado persistido, cargalo y transformalo a dominio antes de ejecutar la regla.

## Mapeo Entre Capas
- Los mappers viven en application o infrastructure segun origen/destino; nunca dentro del dominio puro.
- API DTO <-> command/result suele vivir en el driving adapter HTTP.
- Persistence entity/document <-> domain/application model suele vivir en el driven adapter de persistencia.
- Integration DTO <-> domain/application model vive en el adapter de integracion.
- Los mappings deben ser explicitos cuando nombres, tipos, nullability, unidades, zona horaria, moneda, enum o semantica difieran.
- No confiar en coincidencias automaticas para campos criticos como IDs, tenant, permisos, dinero, fechas, estados, soft delete o version/concurrency.
- El mapping no debe ocultar decisiones de negocio. Si una conversion requiere regla de negocio, esa regla pertenece a dominio/aplicacion y el mapper solo transporta datos.

## Java
- Para Java, seguir `java-stack`: MapStruct es el estandar casi obligatorio para mappings entre capas.
- Usar MapStruct para conversiones repetitivas o con muchos atributos: API DTO, commands, domain, JPA entities y responses.
- Lombok puede usarse en clases Java mutables o gestionadas por frameworks segun `java-stack`; no usarlo para esconder boundaries incorrectos.
- Usar `record` para DTOs y value carriers cuando el framework lo soporte.
- Evitar mappers manuales grandes salvo conversiones triviales o reglas que no deban ser generadas.

## Kotlin
- Para Kotlin, seguir `kotlin-stack`: preferir constructores, named arguments, `copy`, extension functions y funciones puras pequenas.
- No usar Lombok en Kotlin.
- MapStruct en Kotlin es opcional, no default; usarlo solo cuando haya muchos atributos, mappings repetitivos, interoperabilidad Java o convencion previa del proyecto.
- Si se usa MapStruct en Kotlin, justificarlo en la spec o en el patron existente y mantenerlo fuera del dominio puro.
- Evitar escribir Kotlin como Java: no introducir builders verbosos ni getters/setters manuales salvo interoperabilidad estricta.

## Python
- Para Python, seguir `python-stack`: preferir modelos de dominio puros con `dataclass`, clases simples o value objects propios cuando exista logica de negocio.
- Pydantic v2 debe usarse principalmente para DTOs de API, validation schemas, settings y payloads de integracion, no como reemplazo automatico del dominio.
- Si un proyecto pequeno usa Pydantic como modelo interno por simplicidad, la spec debe declararlo como excepcion consciente y asegurar que no se mezclen concerns de API, ORM y dominio.
- No pasar modelos ORM, SQLAlchemy rows, Pydantic request models ni `Request`/`Depends` hacia dominio.
- Los mappers en Python deben ser funciones pequenas, explicitas y testeables, por ejemplo `user_row_to_domain`, `domain_to_user_response` o `create_user_request_to_command`.
- Evitar copias dinamicas con `dict()`, `model_dump()` o `**payload` para mappings criticos si hay cambios de nombre, enums, fechas, dinero, tenant, permisos o nullability.

## FastAPI
- Para FastAPI, seguir `fastapi-stack`: los Pydantic models de `request`/`response_model` pertenecen al adapter HTTP.
- `APIRouter`, `Depends`, `Request`, `BackgroundTasks`, `HTTPException` y security dependencies no deben cruzar hacia application/domain.
- Los endpoints deben convertir `request models` en application commands/queries antes de llamar use cases.
- Los use cases deben retornar domain/application results; el router los convierte a response models.
- SQLAlchemy/Tortoise models, sessions y query builders viven en infrastructure persistence.
- Para repositories async, el port de aplicacion debe expresar comportamiento de negocio, no detalles de `AsyncSession`.
- Los errores deben normalizarse con `fastapi-rest-error-response-standards`, no con payloads default `{"detail": ...}` en contratos publicos.

## Naming y Paquetes
- Los nombres deben revelar capa y proposito: `UserEntity`, `UserDocument`, `CreateUserRequest`, `UserResponse`, `CreateUserCommand`, `UserResult`.
- Evitar nombres genericos como `UserDto` si no queda claro si es request, response, integration payload o application result.
- Mantener paquetes separados por responsabilidad, por ejemplo `domain`, `application`, `infrastructure.persistence`, `infrastructure.web`, `infrastructure.integration`.
- No crear paquetes `dto` globales donde se mezclen contratos de API, persistence projections e integration payloads.

## Paginacion y Consultas
- Los modelos de paginacion externos deben mapearse a queries de aplicacion, no pasar objetos del framework al use case.
- Definir modelos internos como `PageRequest`, `SortCriteria`, `PagedResult` o equivalentes si el proyecto necesita paginacion cross-layer.
- Las optimizaciones de query, fetch joins, projections o native queries viven en infraestructura.
- El contrato HTTP de paginacion debe seguir `restful-standard` y documentarse en OpenAPI.

## Transacciones y Consistencia
- Las transacciones tecnicas pertenecen a application service/use case boundary o configuracion de infraestructura, segun stack.
- No abrir transacciones dentro de mappers.
- No hacer lazy loading desde el dominio.
- No devolver entidades con relaciones lazy hacia capas superiores.
- Si el mapping necesita datos agregados, el repository adapter debe cargar explicitamente lo necesario o devolver un projection mapeado.

## Prohibiciones
- No exponer JPA entities, ORM models, documents o rows como API responses.
- No pasar API DTOs generados por OpenAPI al dominio.
- No retornar framework pagination objects desde output ports.
- No colocar annotations de ORM, JSON, HTTP o validation de transporte en dominio puro.
- No duplicar modelos sin mapping claro entre ellos.
- No introducir mappers "god class" que conozcan todas las capas del sistema.
- No usar reflection/copiers genericos para mappings criticos sin tests y justificacion.
- No convertir `null` en defaults silenciosos si cambia la semantica de negocio.

## Evidencia Esperada
- Lista de modelos por capa y paquete.
- Output ports de aplicacion y adapters de infraestructura que los implementan.
- Mappers identificados por boundary: API, persistence e integrations.
- Reglas de mapping para IDs, enums, fechas, dinero, tenant, auditoria y soft delete.
- Tests o checks para mappings criticos, o `skipped-with-reason`.
- Confirmacion de que dominio no depende de frameworks ni modelos tecnicos.
