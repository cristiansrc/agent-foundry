# Skill: Node.js Stack Convention (IDIOMA: ESPAÑOL)

Este skill define las convenciones de arquitectura y lenguaje para proyectos Node.js con TypeScript y Clean Architecture.

## Base Tecnica
- **TypeScript**: usar `strict` activado, tipos explicitos en boundaries y evitar `any` salvo excepcion justificada.
- **Runtime**: Node.js moderno con ESM cuando el proyecto lo permita; no mezclar module systems sin necesidad.
- **Framework HTTP**: preferir Fastify en proyectos nuevos; Express solo si el proyecto ya lo usa.
- **Validacion**: usar Zod en los puntos de entrada para contratos de request, params, query y env vars.

## Estructura de Carpetas
- **Domain**: `src/domain/` para entidades, value objects y logica de negocio pura.
- **Application**: `src/application/` para use cases, commands, queries, results y output ports.
- **Infrastructure**: `src/infrastructure/` para persistencia, clientes externos, wiring y adapters tecnicos.
- **Interfaces/Web**: `src/interfaces/http/` o `src/web/` para rutas, controllers, middlewares y mappers HTTP.
- **Config**: `src/config/` para configuracion tecnica y bootstrap.
- **Tests**: `tests/` o junto al archivo con `.test.ts` / `.spec.ts`, segun convenga al proyecto.

## Reglas de Boundary
- El dominio no debe importar framework HTTP, ORM, clientes externos, JSON schema ni contenedores de DI.
- Los use cases no deben depender de `Request`, `Reply`, `Response`, `FastifyRequest`, `Express.Request` ni objetos de infraestructura.
- Los DTOs de API pertenecen al adapter HTTP y no deben reutilizarse como dominio por defecto.
- Los output ports viven en `application`; sus implementaciones tecnicas viven en `infrastructure`.

## Persistencia
- Default: una sola capa de persistencia por proyecto, documentada en la spec.
- Relacional: preferir Prisma o Drizzle segun el tipo de servicio; TypeORM solo por excepcion explicita.
- ORM/client/models de persistencia son infraestructura; no exponerlos hacia application/domain.
- Los repositories deben mapear entre modelos tecnicos y domain/application results con funciones explicitas.
- No filtrar `PrismaClient`, query builders, transaction handles ni modelos generados hacia el dominio.
- Si la persistencia es async, mantener el flujo async completo hasta el adapter tecnico.

## Mapping y Modelos
- Separar `command`, `query`, `result`, `request dto`, `response dto` y `persistence model`.
- Usar mappers pequenos y testeables; evitar conversiones por reflexion o copias dinamicas para casos criticos.
- No usar el mismo objeto para API, dominio y persistencia.
- Si una conversion depende de una regla de negocio, esa regla pertenece a dominio o application, no al mapper.

## Testing
- Usar `vitest` o el runner ya establecido por el proyecto.
- Probar use cases sin framework y adapters de persistencia con tests de integracion o contract tests.
- Validar mappings criticos, errores de validacion, estados invalidos y transacciones.
- No dejar DTOs o mappers sin cobertura cuando cruzan boundaries importantes.

## Seguridad y Operacion
- Validar variables de entorno al inicio del proceso.
- Centralizar logging estructurado y trazabilidad en infraestructura.
- No exponer secretos, tokens ni credenciales en config, logs o tests.

## Comportamiento Obligatorio
1. El Executor debe sincronizar OpenAPI desde `docs/api/` a la ruta de infraestructura configurada.
2. Los contratos HTTP deben validarse en el borde con Zod u otra validacion equivalente.
3. La documentacion tecnica debe reflejar la estructura real de `src/domain`, `src/application` e `src/infrastructure`.

## Deteccion del Stack
- Si `package.json` existe y el proyecto es backend sin React ni Angular, este skill se considera **ACTIVO**.
