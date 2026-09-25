# Documentación de cambios híbrida y proporcional al riesgo

## Objetivo

Conservar contratos claros, seguridad y trazabilidad sin exigir el ciclo SDD
completo para todo cambio. La ruta se decide por **riesgo e impacto**, no por
preferencia del agente ni por el número de archivos solamente. Si existe duda,
se usa el nivel superior.

## Decisión de método

Se adopta un flujo propio de Foundry con niveles por riesgo y paquetes compactos;
se toma de [OpenSpec](https://github.com/Fission-AI/OpenSpec) la idea de trabajar
con cambios autocontenidos y deltas, pero no se adopta su CLI ni se reemplazan
los agentes/gates de Foundry. [Spec Kit](https://github.com/github/spec-kit)
mantiene un recorrido explícito de especificar, planificar, descomponer e
implementar, por lo que no es la primera opción para reducir ceremonia.
Los ADR siguen siendo complementarios para decisiones arquitectónicas durables.
ODD (Observability-Driven Development) complementa la documentación con
observabilidad; no sustituye contratos, criterios de aceptación ni gates.

## Clasificación

### Lite — riesgo bajo

Usar para bugs reproducibles cuyo comportamiento esperado ya está definido por
tests, documentación o la petición del usuario, y para refactors internos. No
introducir reglas nuevas ni cambiar contratos, esquema/persistencia, permisos,
integraciones ni arquitectura.

- Entrada: solicitud explícita y acotada del usuario o bug reproducible.
- Agente: `architect-executor`.
- No crear requirements brief, delta spec, planning pack, spec-validator ni task
  board por rutina. El pedido explícito autoriza el alcance; no autoriza ampliarlo.
- Añadir pruebas de regresión cuando aplique; ejecutar la verificación de la
  zona afectada y revisión independiente.
- Si el cambio va a una rama estable, crear el shared context compacto y obtener
  Gate 2 antes de la promoción, como para cualquier otro cambio.

### Standard — riesgo acotado

Usar para un comportamiento visible pero local, implementable como una sola
tarea sin cambiar API pública, esquema/persistencia, autorización, seguridad,
integraciones externas, concurrencia/transacciones críticas ni arquitectura
entre módulos.

- Crear un único `change-brief` basado en `templates/change-brief.md`, guardado
  como `docs/specs/.working/<increment-name>-sdd-context.md`.
- Planner solo participa si el comportamiento o sus criterios de aceptación
  necesitan aclaración; de lo contrario, usar el brief directamente.
- Requiere aprobación humana explícita del brief antes de implementar, pero no
  un ciclo completo de `spec-validator` ni `task-decomposer`.
- Una sola tarea: `architect-executor`; si hacen falta varias tareas, múltiples
  agentes o decisiones de arquitectura, escalar a Full.
- Mantener pruebas, revisión y Gate 2. Documentar solo las decisiones durables.

### Full — riesgo alto, crítico o incierto

Obligatorio ante cambios de OpenAPI/contratos públicos, tablas o migraciones,
datos sensibles, autenticación/autorización, multitenancy, integraciones,
mensajería, reintentos, concurrencia/transacciones, más de un servicio o
boundaries arquitectónicos; también cuando el riesgo no pueda descartarse.

- Aplicar el flujo formal de `spec-driven-development`: requisitos cuando sean
  necesarios, delta spec, artefactos contractuales aplicables, validación,
  Gate 1, descomposición si corresponde, ejecución y calidad.
- `spec-validator` debe dar `verdict: ready` antes de Gate 1 y de la ejecución.
- OpenAPI solo se actualiza si el contrato API cambia. La delta spec documenta
  únicamente dominios aplicables; no rellenar secciones irrelevantes.
- Crear planning context solo cuando haya más de tres archivos relevantes,
  fuentes extensas o contradicciones que requieran curación.
- Crear task board solo cuando se necesite dividir el trabajo entre tareas,
  dependencias o agentes. No descomponer una tarea atómica por ceremonia.

## Reglas de escalamiento

1. Un cambio de alcance, una decisión no resuelta o un hallazgo nuevo puede
   elevar Lite/Standard a Full antes de continuar.
2. No se puede bajar de Full por conveniencia de tokens, urgencia o tamaño del
   diff.
3. Ningún nivel omite tests relevantes, revisión independiente, escaneo de
   secretos aplicable ni Gate 2 para promoción a ramas estables.
4. El brief nunca sustituye OpenAPI, migraciones, configuración de seguridad ni
   otras fuentes contractuales canónicas.
5. Medir tokens por agente y nivel con tareas comparables. No afirmar ahorros por
   cantidad de archivos; comprobar también retrabajo, omisiones, regresiones y
   tiempo de entrega.

## Piloto y evaluación

Probar tareas Lite, Standard y Full con las suites de `evals/cases/`. Registrar
por tarea tokens de entrada/salida por agente, artefactos generados, fallos de
validación, retrabajo posterior, suites ejecutadas y defectos escapados. Ajustar
los umbrales solo con evidencia; conservar evaluaciones de ambigüedad,
escalamiento y protección de contratos.
