---
name: spec-remediation
description: Procedimiento para la corrección iterativa de hallazgos en especificaciones SDD.
---

# Remediación de Especificaciones (Spec Remediation)

Guía para corregir de forma segura y granular los hallazgos reportados por el `spec-validator`. Esta skill no reemplaza a Planner ni a Spec Validator: solo permite resolver hallazgos acotados cuando la fuente autoritativa es clara.

## Precondiciones Obligatorias
- Debe existir un repositorio activo. Si no existe, detener con `Blocked: active repository path required`.
- Debe existir un shared context activo en `docs/specs/.working/<increment-name>-sdd-context.md`.
- Debe existir un reporte o salida reciente de `spec-validator` con hallazgos concretos.
- **Placeholder Guard:** reemplazar siempre `<increment-name>` por el nombre real del incremento. Si el nombre no es claro, preguntar al usuario. Nunca crear archivos con placeholders literales.
- Todo descubrimiento de artefactos debe estar limitado al repositorio activo y a rutas canónicas del shared context. No buscar en `/`, `/home`, `/var`, `/proc`, Docker ni otros proyectos.

## Proceso de Corrección
1. **Rehidratación**:
    - Leer shared context activo, spec activa, OpenAPI, migraciones/config relevantes y último reporte de validación.
    - Verificar que los archivos citados por el hallazgo existen en disco.
     - Si ya no existe, reportar evidencia de `superseded` al orquestador; no
       revalidar contratos por metadata ni cerrar un finding técnico por inferencia.
2. **Clasificación de Hallazgos**: consumir la clasificación y ruta emitidas
   por `spec-validator`:
     - `mechanical` en Markdown autorizado -> `spec-remediator`; OpenAPI ->
       `planner`; migraciones/config -> worker autorizado por orquestación.
     - `technical-decision`, `architectural-decision` o
       `functional-decision` -> `planner`.
     - Un `contract-drift` solo es mecánico si la fuente autoritativa y la
       corrección exacta son inequívocas; en caso contrario va a `planner`.
3. **Priorización**: agrupar hallazgos `mechanical` de la misma causa/fuente
   autoritativa, con rutas y criterios explícitos; mantener IDs individuales.
4. **Corrección Mínima Coherente**: resolver ese lote en todas sus proyecciones
   actuales autorizadas antes de revisión. No agrupar decisiones independientes.
5. **Registro**: actualizar progreso, IDs, archivos y siguiente validación. No
   escribir aprobación. Si scope/permisos impiden completar el lote, bloquear
   por proceso y pedir alcance completo, no validar la mitad sincronizada.
6. **Verificación según impacto**: cambio normativo -> revisión selectiva del
   lote/diff por Spec Validator. Metadata inequívoca -> comprobar proyecciones y
   scan aplicable por worker autorizado, resultado `metadata-verified`, sin
   re-review contractual. No review entre cada cambio mecánico relacionado.

## Correcciones Permitidas
- Normalizar lifecycle/status cuando contradice el veredicto vigente y la evidencia es clara.
- Corregir rutas canónicas erradas cuando el archivo real existe y la intención es inequívoca.
- Sincronizar su representación en Markdown cuando la fuente es explícita.
  No editar YAML/JSON/SQL/scripts/runtime: enviar cambio exacto al editor autorizado.
- Eliminar o marcar como `superseded` findings antiguos que ya no existen en disco.
- Corregir headings obligatorios duplicados o mal nombrados en shared context si no cambia decisiones técnicas.

## Correcciones Prohibidas
- Inventar comportamiento de negocio, reglas de autorización, contratos API, esquemas DB o flujos no especificados.
- Cambiar decisiones de arquitectura, boundaries, transacciones, seguridad, idempotencia o integraciones sin Planner/User.
- Crear, invocar o modificar tareas de implementación como Task Decomposer.
- Invocar o delegar a Executor, Architect Executor, Reviewer, Security Reviewer o Final Validation.
- Marcar `verdict: ready`, escribir `## Spec Validator Approval` por cuenta propia o declarar readiness final.
- Usar `<repo> como ubicación de reportes de proyecto. Los reportes de remediación viven dentro del repositorio activo.

## Reglas de Oro
- **Unidad Coherente**: un lote de misma causa y autoridad; sin rediseño ni mezcla de decisiones independientes.
- **Validación Específica**: re-review normativa sólo por Spec Validator;
  comprobación de metadata/scan no es otra aprobación de readiness.
- **Bloqueo por Modelo**: Si la validación se ejecuta con un modelo no autorizado, se debe detener el proceso con `Blocked: wrong validator model`.
- **Límite de Intentos**: máximo dos rondas por baseline según SDD §10. Si persiste, escribir `<active-repo>/docs/specs/.working/<increment-name>-remediator-bug-report.md` y detener; IDs nuevos no reinician el contador.
- **Alcance**: sólo Markdown documental autorizado; consultas van al orquestador,
  sin delegación anidada ni ampliar permisos por ser mechanical.
- **Decisiones de Diseño**: Si un hallazgo requiere una decisión de arquitectura profunda, debe enrutar al Planner o al Usuario.
- **Routing Guard**: Si falta `change_type`, la ruta no coincide o el hallazgo
  no es `mechanical`, no editar; bloquear y enrutar a `planner`.
- **Estado Conservador**: Si hay duda, bloquear. Una remediación insegura es peor que un hallazgo pendiente.

## Resultado Esperado Por Iteración
Cada iteración debe terminar con uno de estos resultados:
- `metadata-verified`: proyecciones metadata comprobadas; sin cambio normativo,
  sin aprobación nueva ni disposición propia de findings técnicos.
- `fixed-and-awaiting-validation`: se corrigió un hallazgo seguro y falta validación.
- `superseded-finding`: el hallazgo ya no existe en disco y se pide revalidación.
- `blocked-planner-decision`: requiere decisión técnica de Planner.
- `blocked-user-decision`: requiere decisión del usuario.
- `blocked-validator-process-bug`: el hallazgo parece falso positivo o error del validador.
- `blocked-retry-limit`: se agotaron dos rondas y se escribió bug report.
