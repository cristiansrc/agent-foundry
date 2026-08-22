---
name: mysql-standard
description: Estándares y mejores prácticas para el diseño y gestión de bases de datos MySQL.
---

# Estándares MySQL

Guía para el uso eficiente de MySQL (InnoDB) en arquitecturas modernas.

## Configuración y Almacenamiento
- **Engine**: Usar siempre `InnoDB`.
- **Charset**: Usar `utf8mb4` con `utf8mb4_unicode_ci` para soportar todos los caracteres (incluyendo emojis).
- **Naming**: `snake_case` para tablas y columnas.

## Tipos de Datos
- **IDs**: Usar `INT UNSIGNED` o `BIGINT UNSIGNED` con `AUTO_INCREMENT`.
- **Booleans**: Usar `TINYINT(1)` (MySQL no tiene booleano nativo real, usa este alias).
- **JSON**: Usar tipo `JSON` nativo (disponible en MySQL 5.7+).
- **Dates**: Preferir `DATETIME` o `TIMESTAMP` (ojo con el límite de 2038 en `TIMESTAMP`).

## Índices y Rendimiento
- **Primary Keys**: Siempre definir una clave primaria.
- **Composite Indexes**: El orden de las columnas debe seguir el patrón de "más usado a menos usado" y de "mayor selectividad a menor".
- **Prefix Indexes**: Evitar indexar columnas de texto largo completas; usar prefijos si es necesario.

## Restricciones y Limitaciones
- **Foreign Keys**: Definir siempre con nombres explícitos `fk_<tabla_origen>_<tabla_destino>`.
- **DDL No Transaccional**: Tener en cuenta que la mayoría de sentencias DDL en MySQL no son transaccionales (no se pueden revertir con `ROLLBACK`).

## Mejores Prácticas
- Usar `EXPLAIN` para verificar el uso de índices.
- Evitar el uso de `TRIGGERs` y `STORED PROCEDUREs` complejos; preferir lógica en la aplicación.
- Mantener el `innodb_buffer_pool_size` configurado correctamente en producción.
