# Entrega durable de dictámenes — implementación y verificación

## Alcance

Seguimiento del incidente Entralo: resultado de revisión en conversación sin
persistencia completada antes de una interrupción. No se afirma reconstrucción
del dictamen histórico ni se modifica la aprobación humana de Entralo.

Fuentes: protocolo común y SDD §10.1, roles Planner/Orchestrator/Documentation/
Validator/Remediator/Reviewer/Curator/Decomposer/Executor, skills de revisión y
documentación, plantilla de shared y parser de entrega/rondas.

## Decisiones

- Informe literal durable primero; proyecciones y scan después. Sólo continuar
  con entrega complete verificada. Fallo de escritura no es otra review técnica.
- Validador conserva sólo lectura; el escriba no inventa firmas/closures.
- Baseline material separado de metadata; ronda inicial 0 y dos remediaciones.
- Fuente aprobada define intención; código/config/tests evidencian realidad.
- Mechanical no concede permisos: Markdown a Remediator, OpenAPI a Planner.
- Graphify: overlay Foundry de routing, preservando mejoras upstream instaladas,
  sus referencias y archivos locales. No copiar la versión core completa encima.

## Verificación

Los JSON de esta carpeta, cuando se generen, son evidencia del runner contra
salidas nuevas con `--candidate-dir adapters/opencode/out`: agente proyectado
con bindings instalados preservados, skills de candidato y overlay Graphify.
No confundir dry-run con aprobación conductual. Los intentos fallidos se conservan
junto a sus correcciones, sin sobrescribirlos como PASS.

## Resultado al 2026-10-12

- Lint, audit_matrix (0 hallazgos), build de tres adapters y 40 tests deterministas
  PASS. Shared vigente de Entralo pasa parser sin migración ni cambio de HPA.
- Gitleaks filesystem PASS (cero findings); git diff --check PASS.
- Orchestrator 10/10 (`orchestrator-final.json`); escape de evidencia irrecuperable
  con presupuesto agotado repetido 2/2 (`orchestrator-budget-repeat.json`). El primer
  intento proponía recuperar una fuente ya ausente: regla y fixture corregidos.
- Spec Validator 4/4 y convergencia 6/6; Reviewer 2/2; Remediator 2/2; Planner 1/1;
  Executor 4/4; Enterprise Architect 2/2; Final Validation 3/3.
- Curator 2/2 con expediente inline corregido (`curator-inline.json`); intento
  previo agotó timeout al buscar fuentes que el fixture no declaraba ausentes.
- Decomposer: tres casos PASS registrados en `task-decomposer-explicit-config.json`
  antes del límite externo del comando; cuarto guard PASS individual en
  `task-decomposer-delivery-guard.json`. Timeouts 120s previos conservados, no PASS.
  Caso positivo anterior era incompleto; se reemplazó por bootstrap autocontenido.
- Documentation: recuperación filesystem completada (`documentation-final.json`),
  `file_checks.pass: true`: informe/contrato byte-exactos, shared/gates actualizados,
  ronda preservada y sin HPA. Marcada FAIL por matcher que no toleraba Markdown
  en el recibo; matcher corregido sin relajar comprobación de archivos. El intento
  posterior `documentation-verified.json` agotó 180s antes de entrega completa.
  Metadata durante espera HPA pasó caso individual (`documentation-format-fixed.json`).

El cierre inicial dejó instalación bloqueada por timeout. Ese estado queda
supersedido por la verificación y sincronización siguientes; los intentos fallidos
anteriores permanecen como evidencia de sus cortes.

## Activación verificada — 2026-10-12

- Petición humana explícita de commit y actualización OpenCode.
- Nuevo intento de recuperación: 300s agotados (`documentation-activation.json`),
  sin presentarlo como PASS. Logs muestran lecturas y espera de stream del modelo;
  causa de latencia no confirmada. Comprobación final con timeout estándar del
  runner (900s) **PASS**, incluidos artefactos reales: informe/contrato byte-exactos,
  shared/gates coherentes, ronda conservada y sin HPA inventada. Evidencia:
  `documentation-standard-timeout.json`.
- Caso metadata/HPA actual **PASS**: `documentation-metadata-activation.json`.
  No se alteraron contratos/expectativas de archivos para lograr PASS ni modelos.
- Ejecutado `tooling/sync.sh --workflow-only`, backup
  `opencode-workflow-pre-sync-20261012-003329.tar.gz` bajo
  `$HOME/.local/share/agent-foundry/backups/`.
- Comprobación post-sync **PASS** (`sync-verification.json`): 23 agentes y 12
  skills de workflow; bindings modelo/variant/temperature preservados; config,
  plugins, skills ajenas y mejoras/referencias upstream de Graphify intactos.
  Graphify recibe sólo overlay de routing, por eso conserva diferencia deliberada
  frente a la copia core completa.
- Configuración instalada en disco. **Reiniciar OpenCode** para cargarla: las
  sesiones abiertas no se actualizan en caliente. Codex/Kiro sólo salidas generadas.

Riesgo residual: latencia variable en llamadas del modelo/harness; los timeouts
no prueban un rechazo de negocio ni se ocultan. El commit solicitado versiona
fuentes y evidencia; no cambia el negocio ni firmas humanas de Entralo.

## Límites

El parser verifica estructura, existencia del informe y presupuesto explícito;
no autentica firmas, no prueba hashes de producto ni impide por sí solo a un LLM
inventar un baseline. Los casos inline prueban decisiones de routing. El caso
filesystem prueba recuperación con informe original intacto y shared/gates
actualizados, no simula una caída real del proceso ni certifica todos los modelos.
