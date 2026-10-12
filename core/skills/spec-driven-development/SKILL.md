---
name: spec-driven-development
description: Ciclo de vida de desarrollo basado en especificaciones (Master Specs e Incrementos). Asegura que el código siempre esté alineado con la documentación, ya sea en proyectos nuevos, nuevas funcionalidades o modificaciones.
---

# Spec-Driven Development (SDD) Incremental

Esta skill define el estándar para la creación y evolución de especificaciones técnicas en sistemas existentes. Su objetivo es impedir que Planner, Spec Validator, Task Decomposer o Executor avancen con artefactos ambiguos, contradictorios o no verificados en disco.

## 0. Roles y Ownership
- `requirements-analyst`: levanta requerimientos funcionales cuando la solicitud aun no está lista para SDD formal. No escribe OpenAPI, migraciones, specs incrementales formales, task boards ni código.
- `planner`: dueño de specs, contratos OpenAPI, decisiones técnicas, restricciones de arquitectura y shared context durante planificación.
- `spec-validator`: dueño del veredicto de readiness; entrega informe. Documentation persiste/transcribe sin cambiar el dictamen ni corregir decisiones técnicas por inferencia.
- `spec-remediator`: corrige Markdown mecánico con fuente inequívoca. OpenAPI
  sigue en Planner; migraciones/config en worker autorizado. No invoca otros roles.
- `task-decomposer`: dueño exclusivo del task board después de `ready` vigente y Gate 1 humano del mismo alcance.
- `executor`: implementa desde task board/spec aprobados; no toma decisiones de arquitectura ni reinterpreta contratos.
- `final-validation`: valida cumplimiento final contra intención original, specs, contratos, seguridad, tests y documentación.

## 1. Proyectos Nuevos (Greenfield)
El agente debe generar una `Master Spec` inicial que cubra el objetivo, contratos, modelo de datos y reglas de negocio globales.

## 2. Desarrollo Incremental (Nuevas Funcionalidades)
Para añadir características a un sistema existente:
1. **Delta Spec:** Crear un archivo de incremento en `docs/specs/increments/` (ej. `002-feature-name.md`).
2. **Impacto:** Describir qué partes de la `Master Spec` se ven afectadas o extendidas.
3. **Contrato:** Actualizar el `openapi.yaml` antes de tocar el código.
4. **Validación:** El `spec-validator` debe asegurar que el incremento no rompa reglas core.
5. **Contexto Compartido:** Mantener un único archivo activo en `docs/specs/.working/<increment-name>-sdd-context.md`.
6. **Task Board:** Crear `docs/specs/tasks/<increment-name>-task-board.md` solo tras `ready` vigente y Gate 1 humano del mismo alcance.
7. **Grafo de Dependencias:** Si Graphify está configurado, usar `graphify-out/GRAPH_REPORT.md` para mapear dependencias y prever impactos en la estructura de la solución.

**Placeholder Guard:** reemplazar siempre `<increment-name>` por el nombre real del incremento (ej. `user-auth`, `invoice-export`). Si el nombre no es claro, preguntar al usuario. Nunca crear archivos con placeholders literales.

## 3. Modificación de Funcionalidades Existentes
Cuando se cambia el comportamiento actual:
1. **Razonamiento:** Documentar por qué el comportamiento actual ya no es válido.
2. **Refactor Plan:** Detallar los cambios en los puertos y adaptadores para mantener la integridad hexagonal.
3. **Consolidación:** Al finalizar, los cambios deben fusionarse en la `Master Spec` para que esta siempre represente el estado real del sistema.

## 4. Fases Obligatorias por Incremento
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

## 5. Gates Obligatorios
- No ejecutar `task-decomposer` si la spec o el shared context están en `planning`, `draft`, `validator-review`, `revision-needed` o `implementation-blocked`.
- Solo se permite descomposición tras `ready` vigente y aprobación humana de ese plan; `validated-not-executed` por sí solo no libera Gate 1.
- La aprobación debe existir en el shared context como heading exacto `## Spec Validator Approval`.
- El bloque de aprobación debe contener exactamente: `verdict: ready`, `reviewed_at`, `validator_agent: spec-validator`, `artifact_set_reviewed`, `summary` e `invalidated_by_changes_since: none`.
- **Solution Workspace Gate:** En Solution Workspaces (bajo `projects/`), si la especificación modifica contratos OpenAPI expuestos, esquemas de bases de datos compartidas o integraciones entre servicios, es obligatorio que el agente `enterprise-spec-validator` apruebe la alineación global otorgando el veredicto de `Workspace Aligned` en la Master Spec global del Workspace antes de descomponer o ejecutar.
- **Gate de Aprobación Humana de Plan:** Se prohíbe a `task-decomposer` o `executor` iniciar cualquier tarea de implementación si en el Shared Context no existe el encabezado explícito `## Human Plan Approval: approved_by_user`. Si falta, el estado queda bloqueado en `awaiting-human-plan-approval`.
- **Gate de Aprobación Humana de QA (Cierre):** Se prohíbe realizar fusiones a ramas estables (`develop`, `qa`, `master`) si en el Shared Context no existe el encabezado explícito `## Human QA Approval: approved_by_user`. Si falta, el estado queda bloqueado en `awaiting-human-qa-approval`.


- Frases narrativas como `Ready for Task Decomposer`, `Artifacts aligned`, `all findings resolved` o `Current readiness validated-not-executed` no son aprobación válida.
- El dictamen **vigente** usa `ready` o `revision-needed`. `not ready` histórico se interpreta como rechazo, nunca como estado canónico nuevo; dictámenes superseded no gobiernan el incremento actual. El rechazo vigente exige corrección y re-review, no implementación.
- No se permite declarar una inconsistencia como resuelta sin verificar el archivo autoritativo real.
- No se permiten frases como `Known Technical Debt`, `Override Approved by User` o `fix post-increment` para saltarse inconsistencias de spec/OpenAPI/migraciones, salvo aprobación explícita del usuario registrada en el shared context.
- Debe existir un único shared context activo por incremento; contextos anteriores deben marcarse como `superseded` o históricos.
- El task board solo puede usar estados `todo`, `in_progress`, `done` o `blocked`, tanto en estado superior como en tareas.
- Estados como `decomposition-ready`, `validator-approved`, `ready`, `planning`, `executing`, `pending` o `ready-for-decomposition` están prohibidos en task boards.
- Después de aprobación de Spec Validator y antes de que Executor empiece, el estado superior del task board debe ser `todo`.
- Si un task board contiene `Blocker:` o estado superior `blocked`, no puede tener tareas de implementación ejecutables en `todo`; esas tareas deben quedar `blocked` hasta que Planner/Spec Validator resuelvan el contrato.
- Excepción pre-descomposición: un task board bloqueado únicamente por `Awaiting Spec Validator approval` no invalida la spec por sí mismo si todas sus tareas de implementación están `blocked`. Debe tratarse como artefacto pendiente/stale que `task-decomposer` reescribirá o desbloqueará después de `verdict: ready`.
- Antes del primer `verdict: ready`, el task board no debe ser evidencia obligatoria de readiness de la spec. Si aparece, debe listarse como `Pending execution artifact` o histórico, no como contrato canónico requerido.
- La spec no puede tener afirmaciones de ciclo de vida contradictorias: si el encabezado dice `planning` o `draft`, ningún footer o resumen puede decir `validated-not-executed`, `Listo para Task Decomposer` o equivalente.
- Un cambio **material** de reglas, contratos, transacciones, seguridad, integración, prerrequisitos o runtime después de `ready` invalida su cobertura afectada. Registrar razón/alcance y volver a review. Transcripciones exactas de dictámenes, índices, rutas históricas o firmas sin cambio normativo no invalidan contratos: verificar/scanear el delta documental y mantener identidad del set revisado.
- `ready with minor changes` no autoriza descomposición ni ejecución. Solo `verdict: ready` exacto autoriza avanzar.

## 5.1 Alcance de Búsqueda en Filesystem
- Nunca buscar artefactos desde la raíz del filesystem `/`.
- Toda búsqueda debe limitarse al repositorio activo o a rutas canónicas explícitas del shared context.
- **Jerarquía de Solución**: identificar workspace por instrucciones, landscape, ownership y contratos inter-proyecto explícitos. El nombre físico `projects/` no es condición necesaria ni suficiente. No inventar una solución enterprise si no existe evidencia de coordinación multi-proyecto.
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
- Graphify y packs son índices derivados, no contratos normativos. Referenciarlos como navegación cuando sean relevantes; verificar fuentes materiales directamente si stale. No bloquear por frescura de cache cuando la fuente necesaria está identificada y comprobada.
- El shared context no debe duplicar headings obligatorios como `## Spec Validator Approval` o `## Next action`; duplicarlos vuelve ambiguo el estado real.

## 7. Shared Context Mínimo
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

Si falta `## Artifact evidence` o `## Spec Validator Approval`, el incremento no está listo para descomposición ni ejecución.

## 8. Formato Mínimo de Task Board
El task board debe ser creado o reescrito por `task-decomposer` después de `ready` vigente y Gate 1 humano del mismo alcance, y debe incluir:
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

## 10. Convergencia de planificación y revisión

Estas reglas aplican a Planner, Curator, Remediator, validadores y orquestación.
No eliminan gates ni permiten aprobar por agotamiento de intentos.

### Baseline, fase y alcance

- Planificar un slice vertical o bootstrap verificable; la arquitectura global
  delimita dependencias, no obliga a especificar toda V1 como un único gate.
- Antes de review, registrar baseline material, artefactos, criterios de salida
  y decisiones cerradas. Cada gate declara fase: diseño, bootstrap, ejecución
  o go-live. Sólo son prerrequisitos los aplicables al siguiente trabajo.
- Una prueba que necesita un artefacto aún inexistente es aceptación posterior,
  no prerrequisito de crear ese artefacto. Si falta evidencia de compatibilidad,
  proponer spike separado, acotado y aprobado con resultado reproducible; no
  autoriza código de negocio ni producción bajo un plan rechazado.
- Cambios de alcance tras aprobación crean delta explícito. Preservar decisiones
  y firmas históricas, sin transferirlas como aprobación del plan enmendado.

### Estado único y evidencia

- Un solo `Current status`, `Lane`, `Spec Validator Approval` y `Next action`
  actuales por shared. Dentro de Current status, declarar primero `state: <enum>`.
  Historia y dictámenes anteriores viven en informes fechados referenciados.
- Separar set normativo (spec/contratos/reglas/config material) de metadata
  (packs, informes, transcripciones, firmas). Un informe no se incluye dentro
  del snapshot que ese mismo informe pretende certificar.
- El registro de un resultado no es una modificación de lo probado. Si hashes
  normativos no cambian, revisar/scanear metadata nueva sin repetir contratos.
- Evidencia en custodia durable identificada por ruta, fecha, alcance y hashes;
  staging temporal no es custodia. Evidencia nueva no reconstruye un run perdido.
- Actualizar todas las proyecciones actuales del mismo hecho en un lote lógico
  autorizado. Si permisos impiden completar el lote, declarar el bloqueo de
  proceso y solicitar su scope completo, no revisar una actualización a medias.

### Hallazgos y presupuesto

- **Trazabilidad mínima útil:** decisión vigente + fuente verificable + resultado
  de prueba aplicable. Contadores de refresh, conteos de líneas/nodos, duplicación
  de enlaces, formato preferido o prosa histórica no son criterios de readiness.
  Resolverlos como mantenimiento documental sin otra ronda global. Sólo bloquea
  falta de trazabilidad que impida conocer contrato/alcance autorizado, comprobar
  cobertura real o implementar de forma segura; explicar ese impacto concreto.
- La revisión prioriza negocio, contratos, integridad transaccional, seguridad
  y arquitectura del trabajo siguiente. No crear protocolos de procedencia más
  complejos que el cambio ni exigir reconstruir toda la historia para avanzar.
- Finding con ID estable, evidencia exacta, riesgo concreto, fase bloqueada,
  change_type/owner y criterio reproducible de cierre. Low/nits no bloquean por
  presentación; severidad mayor exige impacto real, no preferencia del revisor.
- Re-review comprueba fixes y diff/dependencias afectadas. Reabrir uno cerrado
  sólo por regresión material o riesgo omitido demostrado, citando evidencia
  nueva; no cambiar ID para reiniciar contador.
- Máximo **dos rondas de remediación + re-review por baseline**. Si no converge,
   detener con `blocked`, informe de escape y arbitraje/recorte humano. No tercera
   ronda automática, no `ready` forzado, no override silencioso.
- La revisión inicial usa `remediation_rounds: 0`; re-review normativa tras
  remediación consume 1 o 2. Registrar antes de despachar para no perder conteo
  si la sesión falla. Una repetición técnica por evidencia perdida respeta ese
  presupuesto; recuperar/persistir/normalizar metadata no consume rondas.
- Baseline identifica alcance/set normativo (release/hash si disponible), no
  contador de pack ni hash de informe. Nuevo baseline sólo por delta material
  explícito y revisado; registrar razón y enlace al anterior. Renombrar findings,
  cambiar revisor/sesión o perder evidencia no resetea presupuesto. Si el contador
  histórico es desconocido, recuperar registros o arbitrar; no asumir cero.
- No preguntar nuevamente decisiones cerradas. Insumos humanos que bloquean el
  siguiente paso se piden entonces, agrupados, sin esperar un gate imposible.

### Regla de pausa humana

- Continuar automáticamente por defecto: informes/handoffs/subagentes son pasos
  internos, no solicitudes de confirmación.
- Pausar sólo en `awaiting-human-plan-approval`, `awaiting-human-qa-approval`
  del incremento actual, o ante una decisión material no resoluble desde fuentes
  ni por un rol autorizado.
- No pedir HPA anticipada durante planning/revision-needed. `ready` tampoco es
  HPA; al persistirse la firma humana válida, reanudar sin otro “¿continúo?”.
- No detener tareas del board por aprobaciones intermedias no definidas como gate.
  Preguntar sólo lo que cambia la decisión inmediata; agrupar por owner y dejar
   seguimientos no bloqueantes en su backlog.

## 10.1 Entrega durable y recuperación de dictámenes

Aplica a dictámenes de specs, alineación enterprise, API, review, seguridad y
calidad. No cambia el enum de incremento ni añade gates humanos.

1. En el handoff de revisión, identificar incremento, baseline/alcance, ronda y
   ruta de informe separado dentro del repo (`docs/reviews/` o ruta del proyecto).
   Registrar `Review delivery` junto al cambio de estado ya necesario; el informe
   aún inexistente es salida esperada, no artefacto canónico faltante.
2. El rol emite dictamen, findings/disposición, evidencia, limitaciones y siguiente
   acción identificados por ese alcance. No modifica lo que certifica ni afirma
   que su respuesta ya está persistida. Especialistas conservan sus veredictos.
3. El orquestador entrega inmediatamente la salida original completa a
   Documentation con su atribución disponible (agente/fecha/sesión si comprobables).
   Un resumen conversacional sin original no es prueba de aprobación.
4. Documentation escribe primero el informe literal durable, fuera del set que
   certifica, y verifica contenido/ruta. Reutilizarlo si es idéntico; no sobrescribir
   historia con otro dictamen. Si encuentra datos sensibles, detener/redactar con
   limitación explícita, nunca persistir secretos por literalidad.
5. Después completar en lote shared/gates/resúmenes autorizados desde el informe,
   sin inferir cierres o firmas. Con proyecciones fallidas, conservar el informe y
   `delivery_status: report-persisted`; enumerar pendientes en Next action. Sólo
   `complete` tras comprobar lote/scan aplicable. La entrega no es transacción
   filesystem multiarchivo: no declarar atomicidad física que no existe.
6. El orquestador comprueba informe/alcance y recibo; sólo entonces continúa,
   enruta remediación o pide HPA/QA. Un ready sólo en chat no habilita tareas.
   No rotar voluntariamente con dictámenes pendientes de entrega.

Registro compacto actual por shared (cada nueva entrega reemplaza el registro,
historia queda en informes; el presupuesto del baseline se conserva):

```markdown
## Review delivery
baseline_id: <identidad del alcance material>
baseline_scope: <slice/set revisado>
remediation_rounds: 0
delivery_status: pending
report_path: docs/reviews/<informe-de-esta-revision>.md
```

`delivery_status`: `pending` (sin informe verificado), `report-persisted`
(informe verificado, proyecciones/scan pendientes), `complete` (entrega verificada).
No son estados de incremento ni veredictos. En pending mantener estado de review;
al completar transcribir la transición que el dictamen permite. Revisión técnica
distinta dentro del baseline no borra rondas de remediación consumidas.

**Recuperación idempotente tras interrupción:**
- Informe existe y cubre baseline -> verificarlo y completar proyecciones; ninguna
  review nueva por fallar una escritura. No sobreescribir correcciones posteriores.
- Sólo salida original recuperable -> persistirla con atribución real y completar
  lote; no convertir una memoria resumida en fuente primaria.
- Ni informe ni salida recuperables -> declarar evidencia ausente y coordinar
  review nueva acotada del alcance actual, sin fabricar el resultado perdido.
  Respetar presupuesto/arbitraje. Evidencia temporal no es custodia durable.
- Si cambió el set material desde el dictamen, recuperar historia pero no aplicar
  esa aprobación al delta: revisión selectiva de cobertura afectada.

**Migración:** contextos previos sin este bloque no se rechazan sólo por formato;
comprobar el dictamen fuente vigente y adoptar registro en el siguiente handoff.
Ausencia de fuente/autoridad real sí exige recuperación. `Review delivery` nunca
pertenece al snapshot normativo ni dispara curación/revalidación por sí mismo.
