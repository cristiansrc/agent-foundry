---
name: flyway-migrations
description: Gestión de esquemas de base de datos mediante migraciones incrementales con Flyway. Compatible con PostgreSQL, MySQL, Oracle y SQL Server.
---

# Gestión de Base de Datos con Flyway

Uso de migraciones versionadas y repetibles para garantizar la evolución segura y controlada del esquema de base de datos.

## Tipos de Migraciones
- **Versionadas (V)**: `V<VERSION>__<desc>.sql`. Evolución del esquema. Inmutables una vez aplicadas.
- **Repetibles (R)**: `R__<desc>.sql`. Para objetos que se pueden recrear (Vistas, Procedures, Funciones). Se ejecutan cada vez que cambia su checksum.
- **Undo (U)**: `U<VERSION>__<desc>.sql`. Opcionales, para revertir cambios de una versión específica.

## Reglas de Nomenclatura y Estructura
- Formato: `V1.0.1__create_users.sql` (Usar puntos para subversiones).
- Ubicación estándar: `src/main/resources/db/migration/`.
- **Idempotencia**: Preferir scripts que puedan ejecutarse varias veces sin fallar (ej: `CREATE TABLE IF NOT EXISTS`).

## Gestión del Esquema
- **Propiedad del Esquema**: Flyway es el único dueño. JPA `ddl-auto` debe ser `validate` o `none`.
- **Integridad**: Definir explícitamente Índices, FKs, NOT NULL, UNIQUE y CHECK constraints.
- **Bloqueo de Tareas**: Cualquier cambio de esquema asumido en specs DEBE existir como archivo de migración real antes de pasar a `executor`.
- **Consistencia de Rutas**: Verificar la ruta exacta (`classpath:` vs `filesystem:`) configurada en el proyecto.

## Mejores Prácticas Avanzadas
- **Transaccionalidad**: Flyway envuelve cada migración en una transacción (si el motor lo soporta). Evitar mezclar DDL y DML en motores que no soportan DDL transaccional (ej: MySQL/Oracle para ciertos objetos).
- **Callbacks**: Usar SQL callbacks (`beforeMigrate.sql`, `afterMigrate.sql`) para tareas de configuración de entorno.
- **Validación de Checksums**: Si hay errores de validación, usar `flyway repair` solo si se está seguro de que el cambio en la migración aplicada es correcto y necesario.
- **Vendor Specifics**: Consultar skills específicas para optimizaciones del motor:
    - [postgresql-standard](../postgresql-standard/SKILL.md)
    - [mysql-standard](../mysql-standard/SKILL.md)
    - [oracle-standard](../oracle-standard/SKILL.md)
    - [sqlserver-standard](../sqlserver-standard/SKILL.md)

## Verificación
- Antes de implementar lógica de persistencia, leer físicamente el directorio de migraciones para confirmar la existencia de los artefactos.
