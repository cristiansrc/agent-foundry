---
name: zero-downtime-migrations
description: Patrones de evolución de esquemas relacionales sin tiempo de inactividad utilizando el patrón Expand/Contract, índices en segundo plano y migraciones seguras en Flyway.
---

# Zero-Downtime Database Migrations (Patrón Expand / Contract)

Guía metodológica para el agente `database-architect` e implementadores para realizar migraciones de esquemas relacionales (PostgreSQL, MySQL, Oracle, SQL Server) en caliente, sin requerir ventanas de mantenimiento ni causar caídas del servicio.

---

## 1. El Principio Expand / Contract (Ampliación / Reducción)

Cualquier cambio destructivo o incompatible (renombrar columnas, eliminar campos, cambiar tipos o agregar restricciones `NOT NULL`) **NUNCA** debe realizarse en un solo script ni en una sola versión de despliegue. Debe dividirse en 3 fases:

```
Fase 1: EXPAND (Ampliación) ➔ Fase 2: PARALLEL RUN (Tránsito) ➔ Fase 3: CONTRACT (Reducción)
```

---

## 2. Escenarios Comunes y Solución Paso a Paso

### Escenario A: Agregar una Columna Obligatoria (`NOT NULL`)

1. **Fase 1 (Expand)**: Crear la columna permitiendo `NULL` (o con un valor por defecto temporal).
   ```sql
   -- V1__add_phone_column_expand.sql
   ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL;
   ```
2. **Fase 2 (Transition)**: Desplegar la nueva versión de la aplicación que escribe en `phone`. Ejecutar un script de migración de datos (*backfill*) para llenar los registros antiguos.
3. **Fase 3 (Contract)**: Agregar la restricción `NOT NULL` una vez que todos los registros están llenos.
   ```sql
   -- V2__set_phone_not_null_contract.sql
   ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
   ```

### Escenario B: Renombrar una Columna (`old_name` ➔ `new_name`)

1. **Fase 1 (Expand)**: Crear `new_name` permitiendo `NULL`.
2. **Fase 2 (Parallel Run)**: 
   - El código escribe en ambas columnas o usa un Trigger / Listener de base de datos para sincronizar `old_name` y `new_name`.
   - Ejecutar script de copia de datos históricos de `old_name` a `new_name`.
3. **Fase 3 (Contract)**: Desplegar versión de código que solo lee de `new_name`. En la siguiente versión de BD, eliminar `old_name`.

---

## 3. Creación de Índices sin Bloqueo de Tablas

- **PostgreSQL**: NUNCA usar `CREATE INDEX` simple en tablas de alto tráfico. Usar **`CREATE INDEX CONCURRENTLY`** fuera de bloques de transacción.
  ```sql
  -- Flyway: debe configurarse executeInTransaction=false para este script
  CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
  ```
- **MySQL / InnoDB**: Usar `ALGORITHM=INPLACE, LOCK=NONE`.

---

## 4. Reglas Estrictas de Seguridad en Flyway

- 🚫 **PROHIBIDO**: `DROP TABLE`, `DROP COLUMN`, `ALTER TABLE RENAME` en scripts de fase inicial.
- 🚫 **PROHIBIDO**: Migraciones que ejecuten consultas pesadas sobre millones de filas dentro de la transacción de inicio de la app. Usar scripts asíncronos de datos (*background backfill*).
- ✅ **MANDATORIO**: Todo script Flyway debe probarse de forma idempotente y validar rollbacks antes de promover a `develop`.
