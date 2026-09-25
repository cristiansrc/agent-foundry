---
name: spec-driven-development
description: Documentación de cambios proporcional al riesgo con ruta Lite, Standard y SDD Full para mantener calidad sin artefactos innecesarios.
---

# Documentación Híbrida de Cambios (SDD proporcional al riesgo)

Esta skill define documentación y gates proporcionales al riesgo. No todos los
cambios requieren el ciclo SDD completo. La ruta Full conserva las garantías
formales; Lite/Standard reducen artefactos, no pruebas ni responsabilidad.
La política operativa y el árbol de decisión están en
`docs/runbooks/hybrid-change-documentation.md`.

## Clasificación obligatoria del cambio

Antes de enrutar, clasifica `Lite`, `Standard` o `Full` y registra una razón
breve cuando se cree un artefacto persistente. Ante duda, usa el nivel superior.

- **Lite:** bug reproducible cuyo comportamiento esperado ya está definido, o
  refactor interno; sin regla nueva ni cambio de contrato, datos, permisos,
  integración o arquitectura.
- **Standard:** cambio visible acotado a una sola tarea y módulo, sin API pública,
  persistencia, autorización, integración entre servicios ni decisiones de alto
  impacto. Usa `templates/change-brief.md` y aprobación humana del brief.
- **Full:** cambio de contratos/API, datos/migraciones, seguridad, integraciones,
  concurrencia/transacciones críticas, varios servicios o arquitectura; también
  cambios con riesgo incierto. Aplica el ciclo SDD formal.

Escala en cualquier momento si aparece un contrato afectado, decisión faltante,
riesgo no contemplado o necesidad de varias tareas/agentes. Nunca bajes de Full
por costo, urgencia o tamaño del diff.

## 0. Roles y Ownership del flujo Full
- `requirements-analyst`: levanta requerimientos funcionales cuando la solicitud aun no está lista para SDD formal. No escribe OpenAPI, migraciones, specs incrementales formales, task boards ni código.
- `planner`: dueño de specs, contratos OpenAPI, decisiones técnicas, restricciones de arquitectura y shared context durante planificación.
- `spec-validator`: dueño del veredicto de readiness. Puede actualizar reportes de validación y metadatos de lifecycle/status, pero no debe corregir decisiones técnicas.
- `spec-remediator`: corrige hallazgos mecánicos o drift con fuente autoritativa inequívoca. No invoca Task Decomposer ni Executor.
- `task-decomposer`: dueño exclusivo del task board y de la atomización de tareas después de `validated-not-executed`.
- `executor`: implementa desde task board/spec aprobados; no toma decisiones de arquitectura ni reinterpreta contratos.
- `final-validation`: valida cumplimiento final contra intención original, specs, contratos, seguridad, tests y documentación.

## 1. Proyectos Nuevos (Greenfield) — Full
El agente debe generar una `Master Spec` inicial que cubra el objetivo, contratos, modelo de datos y reglas de negocio globales.

## 2. Desarrollo Incremental (Nuevas Funcionalidades) — según riesgo
Para cambios Lite/Standard sigue la clasificación anterior. Para cambios Full:
1. **Delta Spec:** Crear un archivo de incremento en `docs/specs/increments/` (ej. `002-feature-name.md`).
2. **Impacto:** Describir qué partes de la `Master Spec` se ven afectadas o extendidas.
3. **Contrato:** Actualizar el `openapi.yaml` antes del código solo si cambia un contrato API.
4. **Validación:** El `spec-validator` debe asegurar que el incremento no rompa reglas core.
5. **Contexto Compartido:** Mantener un único archivo activo en `docs/specs/.working/<increment-name>-sdd-context.md`.
6. **Task Board:** Crear `docs/specs/tasks/<increment-name>-task-board.md` después de Gate 1 cuando la ejecución requiera descomposición; no crear boards para una única tarea atómica.
7. **Grafo de Dependencias:** Si Graphify está configurado, usar `graphify-out/GRAPH_REPORT.md` para mapear dependencias y prever impactos en la estructura de la solución.

**Placeholder Guard:** reemplazar siempre `<increment-name>` por el nombre real del incremento (ej. `user-auth`, `invoice-export`). Si el nombre no es claro, preguntar al usuario. Nunca crear archivos con placeholders literales.

## 3. Modificación de Funcionalidades Existentes — Full cuando cambie comportamiento contractual
Cuando se cambia el comportamiento actual:
1. **Razonamiento:** Documentar por qué el comportamiento actual ya no es válido.
2. **Refactor Plan:** Detallar los cambios en los puertos y adaptadores para mantener la integridad hexagonal.
3. **Consolidación:** Al finalizar, los cambios deben fusionarse en la `Master Spec` para que esta siempre represente el estado real del sistema.

## 4. Cobertura requerida por riesgo

Las áreas siguientes son obligatorias en Full cuando apliquen. En Lite/Standard
documenta solo las que cambian o afectan la decisión; no rellenes secciones con
"no aplica" repetidamente.
- **Contexto:** Relación con specs anteriores.
- **Contratos API:** Definición exacta de endpoints (vía OpenAPI).
- **Modelo de Datos:** Cambios en tablas, índices o entidades (vía Flyway).
- **Lógica de Dominio:** Cambios en Use Cases y Domain Services.
- **Integraciones:** Sistemas externos, colas, workflows, retries, timeouts e idempotencia cuando aplique.
- **Seguridad:** AuthN/AuthZ, permisos, tenant/user boundary, datos sensibles, rate limits y auditoría.
- **Operación:** Logs, métricas, trazas, health checks, configuración y despliegue local.
- **Estrategia de Test y Cobertura:** 
    - Definir herramientas (JaCoCo, pytest-cov, etc.).
    - Configurar exclusiones (DTOs, Configs).
    - Establecer umbrales de fallo (min 85% por archivo testable).
    - El Planner debe incluir tareas explícitas para configurar estas herramientas en el primer incremento de cada proyecto.
- **Criterios de Aceptación:** Checklist para el `final-validation`.

## 5. Gates Obligatorios — flujo Full
- No ejecutar `task-decomposer` si la spec o el shared context están en `planning`, `draft`, `validator-review`, `revision-needed` o `implementation-blocked`.
- Solo se permite descomposición cuando el último veredicto de `spec-validator` es `ready` y el estado es `validated-not-executed`.
- La aprobación debe existir en el shared context como heading exacto `## Spec Validator Approval`.
- El bloque de aprobación debe contener exactamente: `verdict: ready`, `reviewed_at`, `validator_agent: spec-validator`, `artifact_set_reviewed`, `summary` e `invalidated_by_changes_since: none`.
- **Solution Workspace Gate:** En Solution Workspaces (bajo `projects/`), si la especificación modifica contratos OpenAPI expuestos, esquemas de bases de datos compartidas o integraciones entre servicios, es obligatorio que el agente `enterprise-spec-validator` apruebe la alineación global otorgando el veredicto de `Workspace Aligned` en la Master Spec global del Workspace antes de descomponer o ejecutar.
- **Gate de Aprobación Humana de Plan:** En Full se prohíbe a `task-decomposer` o `executor` iniciar implementación sin `## Human Plan Approval: approved_by_user` en Shared Context. Si falta, bloquear en `awaiting-human-plan-approval`. Standard requiere aprobación humana explícita del brief antes de ejecución, sin exigir `spec-validator ready`; Lite usa la solicitud explícita del usuario como autorización del alcance.
- **Gate de Aprobación Humana de QA (Cierre):** Se prohíbe realizar fusiones a ramas estables (`develop`, `qa`, `master`) si en el Shared Context no existe el encabezado explícito `## Human QA Approval: approved_by_user`. Si falta, el estado queda bloqueado en `awaiting-human-qa-approval`.


- Frases narrativas como `Ready for Task Decomposer`, `Artifacts aligned`, `all findings resolved` o `Current readiness validated-not-executed` no son aprobación válida.
- Si cualquier review summary o validator output dice `not ready`, la siguiente acción es corrección por Planner y nueva validación, no implementación ni descomposición.
- No se permite declarar una inconsistencia como resuelta sin verificar el archivo autoritativo real.
- No se permiten frases como `Known Technical Debt`, `Override Approved by User` o `fix post-increment` para saltarse inconsistencias de spec/OpenAPI/migraciones, salvo aprobación explícita del usuario registrada en el shared context.
- En Full debe existir un único shared context activo por incremento; en Standard usar el change brief como contexto compacto. En Lite no crear contexto persistente por rutina; crearlo antes de QA si se requiere promoción estable. Contextos anteriores deben marcarse como `superseded` o históricos.
- El task board solo puede usar estados `todo`, `in_progress`, `done` o `blocked`, tanto en estado superior como en tareas.
- Estados como `decomposition-ready`, `validator-approved`, `ready`, `planning`, `executing`, `pending` o `ready-for-decomposition` están prohibidos en task boards.
- Después de aprobación de Spec Validator y antes de que Executor empiece, el estado superior del task board debe ser `todo`.
- Si un task board contiene `Blocker:` o estado superior `blocked`, no puede tener tareas de implementación ejecutables en `todo`; esas tareas deben quedar `blocked` hasta que Planner/Spec Validator resuelvan el contrato.
- Excepción pre-descomposición: un task board bloqueado únicamente por `Awaiting Spec Validator approval` no invalida la spec por sí mismo si todas sus tareas de implementación están `blocked`. Debe tratarse como artefacto pendiente/stale que `task-decomposer` reescribirá o desbloqueará después de `verdict: ready`.
- Antes del primer `verdict: ready`, el task board no debe ser evidencia obligatoria de readiness de la spec. Si aparece, debe listarse como `Pending execution artifact` o histórico, no como contrato canónico requerido. Lite/Standard de una sola tarea no requieren task board.
- La spec no puede tener afirmaciones de ciclo de vida contradictorias: si el encabezado dice `planning` o `draft`, ningún footer o resumen puede decir `validated-not-executed`, `Listo para Task Decomposer` o equivalente.
- Si Planner cambia specs, OpenAPI, migraciones, reglas de transacción, seguridad, integración, task-board prerequisites o runtime config después de un `verdict: ready`, ese ready queda invalidado. El shared context debe registrar `invalidated_by_changes_since` con la razón y volver a `Spec Validator review`.
- `ready with minor changes` no autoriza descomposición ni ejecución. Solo `verdict: ready` exacto autoriza avanzar.

## 5.1 Alcance de Búsqueda en Filesystem
- Nunca buscar artefactos desde la raíz del filesystem `/`.
- Toda búsqueda debe limitarse al repositorio activo o a rutas canónicas explícitas del shared context.
- **Jerarquía de Solución**: Solo aplica cuando el repositorio actual está dentro de una carpeta llamada exactamente `projects/`. Si el padre no es `projects`, el proyecto es STANDALONE y no debe forzarse documentación enterprise ni Master Spec global.
- Shared contexts: buscar solo en `<repo>/docs/specs/.working/`.
- Task boards: buscar solo en `<repo>/docs/specs/tasks/`.
- OpenAPI: buscar solo en `<repo>/docs/api/`, `<repo>/src/main/resources/` o ruta canónica.
- Migraciones: buscar solo en la ruta indicada por spec/config (`src/main/resources/db/migration`, `db/migration`, u otra explícita).
- Si falta el repo activo, detener con `Blocked: active repository path required`; no ampliar búsqueda a `/home`, `/`, `/var`, `/proc`, Docker ni otros proyectos.
- Errores de permisos fuera del repo activo son errores del proceso de búsqueda, no hallazgos de validación del proyecto.

## 5.2 Rehidratación Después de Compaction
- Después de compaction, sesión resumida o duda sobre el historial del chat, el agente debe releer artefactos desde disco antes de decidir.
- El resumen compacto del chat es solo una pista; la fuente de verdad son los archivos actuales del repo.
- Releer como mínimo: shared context activo, spec activa, OpenAPI, migraciones/config relevantes, task board si existe y último reporte de validación si existe.
- Si un reporte viejo o resumen de chat contradice los archivos actuales, marcarlo como `superseded` y validar contra los archivos actuales.
- Ningún agente debe aprobar, descomponer o ejecutar basándose solo en memoria conversacional posterior a compaction.

## 6. Evidencia de Consistencia
Todo checklist de consistencia debe incluir:
- Ruta absoluta del artefacto revisado.
- Campo, endpoint, columna, enum o flujo verificado.
- Resultado observado en el archivo real.
- Estado: `pass`, `fail` o `blocked`.
- Ningún artefacto puede marcarse `pass` si el agente no leyó o listó el archivo/directorio real en el ciclo actual.
- Ningún artefacto puede marcarse `pass` si la evidencia contradice el contenido actual del archivo.
- Las rutas canónicas deben distinguir archivos y directorios. Una ruta inexistente en `Canonical artifacts` bloquea la preparación.
- Si Graphify está configurado en el proyecto, el reporte de dependencias (`graphify-out/GRAPH_REPORT.md`) debe incluirse en los `Canonical artifacts` del shared context y verificarse su estado de actualización.
- El shared context no debe duplicar headings obligatorios como `## Spec Validator Approval` o `## Next action`; duplicarlos vuelve ambiguo el estado real.

## 7. Shared Context Mínimo — Full
El shared context debe incluir, como mínimo:
- `## Current status`
- `## Canonical artifacts`
- `## Artifact evidence`
- `## Spec Validator Approval`
- `## Decisions locked`
- `## Validator findings`
- `## Resolved findings`
- `## Open questions`
- `## Stale terms guard`
- `## Next action`

Si falta `## Artifact evidence` o `## Spec Validator Approval`, un incremento Full no está listo para descomposición ni ejecución. Standard usa el formato compacto `templates/change-brief.md`; Lite puede prescindir del archivo hasta cierre/QA.

## 8. Formato de Task Board — cuando hay descomposición
El task board debe ser creado o reescrito por `task-decomposer` después de `validated-not-executed` y debe incluir:
- Ruta absoluta de spec aprobada y shared context usado.
- Estado superior: `todo`, `in_progress`, `done` o `blocked`.
- Tareas atómicas con id estable, owner esperado, dependencias, archivos/áreas permitidas, pasos de implementación y verificación.
- Criterios de bloqueo explícitos: `Blocked:` con decisión faltante, artefacto inconsistente o dependencia externa.
- Registro de ejecución: changed files, verification result y notas de implementación.

No debe contener tareas genéricas como "implementar backend" o "crear frontend". Si no se puede descomponer en tareas ejecutables sin decisiones de arquitectura, debe quedar `blocked` y volver a Planner/Spec Validator.

## 9. Cierre y Consolidación
- Al terminar un incremento, actualizar la Master Spec o documentación consolidada solo con decisiones durables.
- Marcar artefactos temporales obsoletos como `superseded` o archivarlos para evitar que contaminen futuras búsquedas.
- El estado final debe distinguir entre `implemented`, `closed` y `superseded`; no reutilizar `validated-not-executed` para incrementos ya ejecutados.
- Al cerrar un incremento, transferir las lecciones aprendidas o bugs técnicos recurrentes al registro de memoria `MEMORY.md` (local o global) para evitar que los agentes los vuelvan a cometer en futuras tareas.

