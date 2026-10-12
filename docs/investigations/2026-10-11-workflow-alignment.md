# Auditoría de alineación del flujo — 2026-10-11

Alcance: 27 prompts SDLC, workflow, profiles/permisos, skills transversales,
adapters y configuración generada. Inspección de instrucciones y controles,
no certificación del comportamiento futuro de todos los modelos.

## Diagnóstico

La primera corrección de convergencia era parcial: varios roles/skills seguían
exigiendo estados obsoletos, re-curación/grafo, producción y correcciones propias
del validador. La instalación aún conservaba prompts anteriores. No bastaba
cambiar Planner/Spec Validator aislados.

## Cobertura por rol

| Roles | Discrepancia o condición | Corrección/resultado en fuentes |
|---|---|---|
| master-orchestrator | Routing incompleto en matrix; Git read-only tratado como mutación | Delegates completo; bloque común y consultas planas; decisión humana oportuna |
| planner | Policy nueva contradicha por skills pinning/pre-flight | Skills alineadas; bash deny significa solicitar ejecución al worker |
| context-curator | Routing a deprecados; grafo como gate | No routing deprecados, refresh material únicamente |
| solution-architect | Sin guard global de convergencia | Protocolo común incorporado sin imponer tecnología/patrones |
| enterprise-architect | Detecta workspace por carpeta, crea repos automáticamente, Keycloak fijo, promete shell denegado | Mapping explícito/proveedor aprobado; ejecución por worker autorizado |
| requirements-analyst | Excluido del harness OpenCode aunque lifecycle lo exigía | Planner puede discovery funcional cuando no instalado; no invocar ruta ausente |
| task-decomposer | Rechazo de cualquier review histórico; orden core antes de tests | Dictamen actual; bootstrap previo al rojo funcional sin invertir TDD |
| test-architect | Exige validated-not-executed después de board; no Gate1; rojo artificial | decomposition-completed/in_progress + ready/Gate1 actuales; tests existentes no se debilitan |
| executor | Rechaza estados normales ejecución; falta salida nueva bloquea greenfield | Estados reales y deps; outputs autorizados no inputs faltantes |
| ui-designer/ui-executor | Sin policy global; UI executor heredaba gate de executor errado | Protocolo común + gate correcto; diseño elegido no se reexplora por rutina |
| database-architect/devops-architect | Workers especializados sin gate común | Mismo scope/gates; no decisiones de producto por permiso amplio de herramientas |
| documentation | Pases de un archivo dejan estados incompatibles | Lote coherente y transcripción, nunca aval técnico propio |
| spec-remediator | Límite de scope no reforzado en permisos | Markdown documental; cambios OpenAPI sólo Planner |
| spec-validator/enterprise-spec-validator | Full edit aunque rol validator; escritura dentro de objeto certificado | edit deny; informe y escriba; fases y metadata por delta |
| api-governance-agent | PASS especializado podía confundirse con readiness | Protocolo común: dictamen API acotado, no ready global |
| reviewer/security-reviewer | Sin policy global; cada review puede reiniciar historia | Protocolo selectivo preservando riesgos técnicos nuevos demostrados |
| final-validation | Producción/cadena completa exigidas en todo incremento | quality por slice; go-live sólo cuando corresponde |
| functional-tester-agent | Prompt exige reportes pero edit deny; skill permite corregir propio resultado | Write sólo reportes; worker corrige; framework/gestor existente |
| bug-diagnostician | No discrepancia crítica propia; routing sin gate podía saltar flujo | Protocolo común, entrega RCA; worker sólo carril autorizado |
| git-executor | Exclusividad incluía inspección de todos los agentes | Mutaciones exclusivas con petición/gates; read-only permitido |
| architect-executor/refactor | Matrix deprecados, cuerpos operativos vigentes, Kiro los genera | Banner no-ejecución + edit/bash deny; no packs activos |
| general | Guardrail excluido de OpenCode; no worker | Task allowlist del orquestador excluye built-ins/rutas no instaladas; no afirmar guard instalado |

## Controles añadidos

- `core/workflow/agent-protocol.md` incorporado por los tres adapters; no 27
  copias manuales divergentes. Defaults de permisos efectivos en OpenCode,
  `task: deny` para roles especializados; orquestador delega sólo22roles instalables, no built-in general/explore ni roles deprecados.
- Auditoría matrix ahora devuelve exit1 con findings (antes exit0 aun fallando).
- Tests de protocolo/permiso/salida junto a regresiones de estados.
- Runner eval sólo evalúa eventos text de respuesta; exit no-cero, timeout o
  no-response nunca aprueban por logs. Diagnóstico parcial y caso/stop-on-error
  evitan llamadas en cascada cuando falla el harness.
- No modificación de bindings/modelos. Evals de roles/casos se ejecutan en
  sandbox; timeout no equivale a rechazo ni se oculta como PASS.
- Kiro/Codex reciben el protocolo; equivalencia fina de permisos scoped depende
  del adapter/harness. Sólo OpenCode tiene perfil operativo certificado previo.
- Secuencia/red-first: board `decomposition-completed` → tests funcionales rojos
  aplicables → ejecución; no pedir rojo artificial de checks existentes.

## Activación

Verificar lint/matrix/build/tests y evals reales afectadas antes de sync según
runbook. Instalación anterior no se actualiza por editar core; reiniciar después
de sync. No commit/push por esta solicitud. Resultados al cierre en el resumen
de entrega y en el informe de recuperación de Entralo.

**Resultado actualizado:** lint/matrix/build PASS,29tests deterministas PASS.
Los seis casos reales `orchestrator-continuation.yaml` pasan con Sol en OpenCode;
el caso HPA/continuación se repitió individualmente después de un timeout aislado
45s y pasó a90s. No certifica todos los modelos/harnesses ni todo comportamiento
de los roles. El sync workflow-only preservó model/variant/temperature, plugin,
config y skills ajenas; backup `opencode-workflow-pre-sync-20261011-223633.tar.gz`.
OpenCode debe reiniciarse. `status.sh` sólo reporta drift previo de `graphify`,
intencionalmente no reemplazado. Entralo conserva su pausa HPA vigente; esto no
aprueba el plan ni inicia código.

Eval acotada adicional: `executor-guardrails` mismatch→Blocked PASS1/1;
`final-validation` PASS3/3; `planner` gate ausente PASS1/1. Los casos de
Task Decomposer con `--executor opencode` agotaron 45s/90s sin respuesta; no se
certifica su salida conductual positiva ni negativa. El dry-run YAML PASS3/3
solo confirma formato. No se ocultó el timeout ni se inició un ciclo automático
de reintentos. El siguiente uso real del Task Decomposer es la tarea que seguirá
a la HPA humana de Entralo; comprobar su salida en esa sesión y, si no responde,
tratarlo como bloqueo de harness/modelo, no como pregunta de negocio.
