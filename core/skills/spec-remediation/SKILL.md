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
    - Si la evidencia del hallazgo no existe en los archivos actuales, marcarlo como `validator/process-bug` o `superseded` y pedir revalidación.
2. **Clasificación de Hallazgos**: 
    - `mechanical`: Errores de formato o metadatos.
    - `contract-drift`: Desajuste entre Spec y OpenAPI/Migraciones.
    - `design-decision`: Ambigüedad en la lógica de negocio.
    - `migration-risk`: Riesgos en cambios de base de datos.
    - `validator/process-bug`: El validador se equivoca.
    - `user-decision`: Requiere intervención humana.
3. **Priorización**: Tomar el primer hallazgo seguro (`mechanical` o `contract-drift`) cuya fuente autoritativa sea inequívoca.
4. **Corrección Mínima**: Aplicar el cambio más pequeño posible para resolver un único hallazgo.
5. **Registro**: Actualizar el shared context solo con progreso de remediación, hallazgo tratado, archivos modificados y siguiente validación requerida. No escribir aprobación.
6. **Re-Validación Selectiva**: Solicitar validación solo de ese hallazgo o del artefacto afectado al `spec-validator` oficial.

## Correcciones Permitidas
- Normalizar lifecycle/status cuando contradice el veredicto vigente y la evidencia es clara.
- Corregir rutas canónicas erradas cuando el archivo real existe y la intención es inequívoca.
- Sincronizar nombres de campos, endpoints, columnas o enums entre spec y OpenAPI/migraciones cuando una fuente autoritativa está explícitamente definida.
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
- **Iteración Granular**: No intentar corregir todos los hallazgos a la vez.
- **Validación Específica**: Las validaciones deben pedirse exclusivamente al agente `spec-validator`, con el modelo asignado en el perfil de ejecución.
- **Bloqueo por Modelo**: Si la validación se ejecuta con un modelo no autorizado, se debe detener el proceso con `Blocked: wrong validator model`.
- **Límite de Intentos**: Máximo 4 intentos por hallazgo. Si persiste, escribir `<active-repo>/docs/specs/.working/<increment-name>-remediator-bug-report.md` y detener el flujo.
- **Alcance**: No puede crear ni llamar a `task-decomposer` ni `executor`. Solo trabaja sobre artefactos SDD (Specs, OpenAPI, Migraciones, Config).
- **Decisiones de Diseño**: Si un hallazgo requiere una decisión de arquitectura profunda, debe enrutar al Planner o al Usuario.
- **Estado Conservador**: Si hay duda, bloquear. Una remediación insegura es peor que un hallazgo pendiente.

## Resultado Esperado Por Iteración
Cada iteración debe terminar con uno de estos resultados:
- `fixed-and-awaiting-validation`: se corrigió un hallazgo seguro y falta validación.
- `superseded-finding`: el hallazgo ya no existe en disco y se pide revalidación.
- `blocked-planner-decision`: requiere decisión técnica de Planner.
- `blocked-user-decision`: requiere decisión del usuario.
- `blocked-validator-process-bug`: el hallazgo parece falso positivo o error del validador.
- `blocked-retry-limit`: se agotaron 4 intentos y se escribió bug report.
