---
name: oracle-standard
description: Estándares y mejores prácticas para el diseño y gestión de bases de datos Oracle.
---

# Estándares Oracle DB

Guía para el desarrollo eficiente sobre Oracle Database.

## Naming y Estructura
- **Naming**: `UPPER_SNAKE_CASE` (es el estándar por defecto de Oracle). Limitar nombres a 30 caracteres (versiones antiguas) o 128 (12.2+).
- **Schemas**: En Oracle, un `USER` es equivalente a un `SCHEMA`.
- **Tablespaces**: Definir tablespaces específicos para datos e índices para optimizar I/O.

## Tipos de Datos
- **Numbers**: Usar `NUMBER` para todo valor numérico. `NUMBER(19,0)` para IDs largos, `NUMBER(1,0)` para boletos.
- **IDs**: Usar `GENERATED ALWAYS AS IDENTITY` (Oracle 12c+) para autoincrementales.
- **Strings**: Usar `VARCHAR2(n CHAR)` para asegurar que el límite es en caracteres y no en bytes (importante para UTF-8).
- **LOBs**: Usar `CLOB` para textos largos y `BLOB` para binarios. Evitar `LONG`.

## Rendimiento e Índices
- **Indexes**: Oracle usa B-Tree por defecto. Considerar `Bitmap Indexes` solo para columnas con muy baja cardinalidad en entornos de Data Warehouse.
- **Sequences**: Usar `CACHE` en secuencias para mejorar el rendimiento de inserción masiva.
- **Execution Plan**: Usar `EXPLAIN PLAN FOR` y `DBMS_XPLAN.DISPLAY`.

## Mejores Prácticas
- Usar `DUAL` para queries que no requieren una tabla real (ej: `SELECT SYSDATE FROM DUAL`).
- Implementar paginación con `OFFSET / FETCH` (Oracle 12c+) en lugar de `ROWNUM` anidado.
- Manejar transacciones explícitamente; recordar que Oracle requiere `COMMIT`.
- PL/SQL debe usarse con moderación, preferiblemente para lógica de datos crítica que requiere atomicidad absoluta.
