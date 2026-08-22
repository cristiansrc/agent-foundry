---
name: sqlserver-standard
description: Estándares y mejores prácticas para el diseño y gestión de bases de datos SQL Server.
---

# Estándares SQL Server (T-SQL)

Guía para el desarrollo eficiente sobre Microsoft SQL Server.

## Naming y Esquemas
- **Naming**: `PascalCase` es común en el ecosistema MS, aunque `snake_case` es aceptable si el proyecto lo requiere.
- **Schemas**: Usar esquemas para agrupar tablas funcionalmente (ej: `Sales.Orders` en lugar de `dbo.SalesOrders`).
- **Quotes**: Usar corchetes `[Table Name]` para identificadores con espacios o palabras reservadas.

## Tipos de Datos
- **IDs**: Usar `INT IDENTITY(1,1)` o `BIGINT IDENTITY(1,1)`.
- **Strings**: Usar `NVARCHAR(n)` para soporte Unicode completo. Evitar `VARCHAR` a menos que el ahorro de espacio sea crítico y no se necesite i18n.
- **Booleans**: Usar tipo `BIT`.
- **Dates**: Usar `DATETIMEOFFSET` para manejar zonas horarias correctamente.

## Índices y Rendimiento
- **Clustered Index**: Generalmente en la clave primaria. SQL Server ordena físicamente los datos basándose en este índice.
- **Non-Clustered Indexes**: Para optimizar búsquedas frecuentes.
- **Included Columns**: Usar `INCLUDE` en índices no clúster para cubrir queries sin añadir columnas a la estructura del árbol del índice.
- **SARGability**: Escribir queries que permitan el uso de índices (evitar funciones sobre columnas en el `WHERE`).

## Integridad y Transacciones
- **DDL Transaccional**: SQL Server permite envolver cambios de esquema (CREATE, ALTER) en transacciones.
- **Foreign Keys**: Definir siempre con `ON DELETE NO ACTION` por defecto para evitar cascadas accidentales, a menos que se requiera explícitamente.

## Mejores Prácticas
- Usar `SET NOCOUNT ON` al inicio de procedimientos para evitar tráfico de red innecesario.
- Evitar el uso excesivo de `Cursors`; preferir operaciones basadas en conjuntos (SET-based).
- Usar `TRY...CATCH` para el manejo de errores en T-SQL.
- Monitorear el rendimiento con `Query Store` y el `Execution Plan` gráfico.
