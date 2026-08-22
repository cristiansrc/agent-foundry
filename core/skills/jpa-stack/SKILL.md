---
name: jpa-stack
description: Convenciones para Jakarta Persistence/Hibernate en Spring Boot: entidades, repositories, auditoria, soft delete, transacciones, locking y performance.
---

# JPA / Hibernate Stack

Esta skill define persistencia JPA/Hibernate para Java/Kotlin. No define dominio ni DTOs de API; la separacion de modelos vive en `repository-dto-patterns` y los boundaries en `hexagonal-architecture`.

## Alcance
- Aplicar cuando el proyecto use Jakarta Persistence, Hibernate, Spring Data JPA o `EntityManager`.
- Las entidades JPA, repositories Spring Data, queries y configuracion ORM pertenecen a infraestructura.
- Los use cases no deben depender de `JpaRepository`, `EntityManager`, `Pageable`, `Page<T>`, `Specification`, `CriteriaBuilder` ni entidades JPA.
- Los adapters de persistencia deben mapear entre entidades JPA y modelos de dominio/application results.

## Entidades JPA
- Las entidades JPA son modelos de persistencia, no modelos de dominio.
- Ubicarlas en infraestructura, por ejemplo `infrastructure.persistence.entity`.
- No exponer entidades JPA en controllers, OpenAPI DTOs, application ports ni dominio.
- Mantener constructors protegidos/sin argumentos solo por requerimiento JPA; usar factories o mappers para crear entidades desde modelos internos.
- Evitar logica de negocio central dentro de entidades JPA. Permitir solo invariantes tecnicas simples de persistencia si no contaminan dominio.
- Evitar `equals`/`hashCode` basados en relaciones lazy. Usar identificadores estables con cuidado o seguir la convencion del proyecto.
- No usar `toString` que navegue relaciones lazy o exponga datos sensibles.

## IDs y Generacion
- Preferir UUID para IDs publicos o entidades expuestas indirectamente fuera del servicio.
- Para PostgreSQL/Oracle, preferir `SEQUENCE` con secuencias dedicadas cuando se requiera performance de inserts y batching.
- Para MySQL, `IDENTITY` es aceptable, entendiendo que puede limitar batching.
- No asumir una estrategia unica cross-database; la spec/migration debe declarar la estrategia real.
- IDs internos secuenciales no deben exponerse como identificadores publicos si hay riesgo de enumeracion.

## Relaciones y Lazy Loading
- Usar `FetchType.LAZY` por defecto en relaciones.
- No devolver entidades con relaciones lazy fuera de infraestructura.
- No acceder lazy relations desde dominio, controllers o serializers.
- Resolver N+1 con `@EntityGraph`, fetch joins, batch size o queries especificas.
- Evitar `EAGER` global salvo justificacion fuerte y documentada.
- Para agregados complejos, cargar explicitamente el grafo necesario en el adapter y mapear a dominio/result.
- No usar Open Session in View como mecanismo para "resolver" lazy loading en API.

## Repositories y Adapters
- Interfaces `JpaRepository` viven en infraestructura.
- Output ports de aplicacion deben expresar capacidades de negocio, por ejemplo `UserLookupPort`, no detalles JPA.
- El adapter implementa el output port y delega a Spring Data JPA/EntityManager.
- Spring Data projections pueden usarse para consultas optimizadas, pero deben mapearse a application results antes de salir del adapter.
- `Pageable` y `Page<T>` pueden usarse dentro de infraestructura; hacia application usar modelos propios como `PageRequest`, `SortCriteria` o `PagedResult`.
- Native queries son aceptables cuando JPQL/HQL no expresa bien el caso o por performance, pero deben estar justificadas y testeadas.

## Mapeo
- Java: usar MapStruct segun `java-stack`, especialmente `Entity <-> Domain/Application`.
- Kotlin: preferir funciones explicitas/extension functions segun `kotlin-stack`; MapStruct solo si esta justificado.
- Los mappers JPA viven en infraestructura o application adapter, nunca en dominio puro.
- Los mappings deben tratar explicitamente IDs, enums, fechas, dinero, tenant, auditoria, soft delete y version/concurrency.
- No usar reflection/copiers genericos para entidades con relaciones, lazy loading o campos sensibles.

## Auditoria
- Toda tabla de negocio debe tener auditoria salvo excepcion documentada.
- Campos recomendados:
  - `created_at`: instante UTC, not null, no actualizable.
  - `updated_at`: instante UTC, not null.
  - `created_by`: identificador de usuario/servicio cuando aplique.
  - `updated_by`: identificador de usuario/servicio cuando aplique.
- En Spring Data JPA, usar `AuditingEntityListener`, `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy` y `@EnableJpaAuditing` cuando aplique.
- Para instantes, preferir `Instant` sobre `LocalDateTime` si representa momento absoluto.
- La auditoria debe estar respaldada por migraciones, no solo annotations.
- No confiar en valores de auditoria enviados por el cliente.

## Soft Delete
- Para datos de negocio recuperables o auditables, preferir soft delete con `deleted_at` o `deleted`.
- `deleted_at` suele ser preferible cuando importa saber cuando ocurrio el borrado.
- Toda query funcional debe excluir registros eliminados salvo caso de auditoria/admin.
- En Hibernate moderno, evaluar `@SQLDelete` + `@SQLRestriction` o filtros Hibernate segun version/proyecto. Evitar depender de reglas obsoletas sin validar compatibilidad.
- Si se requiere consultar eliminados, proveer repository method explicito y protegido.
- Soft delete debe estar reflejado en indices, unique constraints y migrations. Para uniqueness, evaluar partial unique indexes donde el motor lo soporte.
- No mezclar hard delete y soft delete en la misma entidad sin decision documentada.

## Transacciones
- Declarar `@Transactional` en application service/use case boundary o adapter service definido por el proyecto, no en controllers.
- Usar `@Transactional(readOnly = true)` para consultas.
- Mantener transacciones cortas; no envolver llamadas externas lentas dentro de la misma transaccion salvo decision explicita.
- Para flujos con integraciones externas, definir orden transaccional y considerar outbox/inbox o compensacion.
- No abrir transacciones dentro de mappers.
- No depender de lazy loading fuera de la transaccion.

## Locking y Concurrencia
- Usar `@Version` para optimistic locking en entidades con actualizaciones concurrentes.
- Mapear conflictos de version a error funcional, normalmente `409 CONFLICT`.
- Usar pessimistic locking solo cuando exista una necesidad real y se entienda el impacto en throughput.
- Definir orden de locks si hay multiples entidades para evitar deadlocks.
- Las specs deben declarar comportamiento ante conflictos concurrentes.

## Consultas y Performance
- Preferir queries especificas sobre cargar agregados completos innecesarios.
- Usar `@EntityGraph` o fetch join para relaciones requeridas por el caso.
- Usar pagination o streaming para colecciones grandes.
- Definir indices en migrations para filtros, joins y ordenamientos frecuentes.
- Revisar N+1 en endpoints/listados criticos.
- Configurar batch size/fetch size solo con evidencia o necesidad clara.
- No usar native query para saltarse mappings o boundaries.

## Migraciones
- Todo cambio de entidad persistente debe tener migracion correspondiente.
- La migration debe ser fuente de verdad del schema, no `ddl-auto`.
- En ambientes no locales, `spring.jpa.hibernate.ddl-auto` debe estar en `validate` o deshabilitado segun politica del proyecto.
- No usar `update` en entornos compartidos o productivos.
- Las rutas de migracion deben alinearse con `springboot-stack` y la skill de migraciones activa.

## Validacion y Constraints
- Constraints de integridad critica deben existir en base de datos: not null, unique, foreign keys, checks o equivalents.
- Bean Validation en entidades puede existir para proteccion adicional, pero no reemplaza constraints de DB ni validacion de API.
- Validacion de transporte pertenece a DTOs/API; reglas de negocio pertenecen a dominio/aplicacion.
- No poner annotations JSON/OpenAPI en entidades JPA.

## Prohibiciones
- No exponer entidades JPA como API responses.
- No usar entidades JPA como dominio en arquitectura hexagonal.
- No pasar `JpaRepository`, `EntityManager`, `Pageable`, `Page<T>` o `Specification` a application/domain.
- No usar Open Session in View para sostener serialization de entidades.
- No habilitar `ddl-auto=update` como solucion de migraciones.
- No usar `EAGER` para ocultar problemas de N+1.
- No crear relaciones bidireccionales por defecto; usarlas solo si el caso lo necesita.
- No incluir secretos o PII innecesaria en logs de SQL.

## Evidencia Esperada
- Paquetes de entidades, repositories y adapters.
- Estrategia de ID por motor de base de datos.
- Auditoria y soft delete reflejados en entidades y migrations.
- Transaction boundaries y read-only queries identificados.
- Estrategia de locking/concurrencia si aplica.
- Evidencia de queries criticas revisadas por N+1/paginacion/indices.
- Confirmacion de que application/domain no dependen de tipos JPA.
