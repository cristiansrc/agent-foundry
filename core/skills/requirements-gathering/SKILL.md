---
name: requirements-gathering
description: Estándares y estructura para el levantamiento de requerimientos funcionales antes de planificación SDD.
---

# Levantamiento de Requerimientos (Requirements Gathering)

Guía para transformar una solicitud de usuario en un documento de requerimientos funcionales claro y accionable antes de la fase de planificación SDD. Esta skill captura el **qué** y el **por qué**; no diseña el **cómo** técnico.

## Responsabilidad y Alcance
- `requirements-analyst` usa esta skill cuando la intención del usuario es vaga, incompleta o todavía no está lista para Planner.
- El resultado es un Requirements Brief funcional, no una spec SDD formal.
- El brief debe reducir ambigüedad para Planner sin tomar decisiones de arquitectura, API, base de datos, infraestructura o implementación.
- Si el usuario ya trae una spec validada o una tarea técnica concreta, no forzar requirements discovery; pasar al agente/flujo correspondiente.

## El Requirements Brief (`requirements-brief.md`)
Todo levantamiento debe producir un artefacto bajo `docs/specs/requirements/` o `docs/specs/.working/`.

Ruta recomendada:
- `docs/specs/requirements/<increment-name>-requirements-brief.md`
- `docs/specs/.working/<increment-name>-requirements-brief.md` si el proyecto usa contexto temporal.

**Placeholder Guard:** reemplazar siempre `<increment-name>` por el nombre real de la funcionalidad o incremento. Si no es claro, preguntar al usuario. Nunca crear archivos con placeholders literales.

### Estructura Mandatoria
1. **Status**: `requirements-discovery`.
2. **Objetivo**: Qué se busca lograr.
3. **Contexto**: Antecedentes y relación con el sistema actual.
4. **Actores y Permisos**: Quiénes interactúan y qué pueden hacer.
5. **Alcance (Scope)**: Lista detallada de funcionalidades.
6. **No Objetivos (Out of Scope)**: Qué no se hará para evitar el scope creep.
7. **Flujos de Usuario**: Secuencia de pasos principales.
8. **Entidades Funcionales**: Datos clave involucrados.
9. **Integraciones**: Sistemas externos o servicios necesarios.
10. **Seguridad y Restricciones**: Reglas críticas.
11. **Edge Cases**: Escenarios no comunes.
12. **Criterios de Aceptación**: Cómo saber que se cumplió el requerimiento.
13. **Preguntas Abiertas**: Dudas para el Usuario/Planner.
14. **Supuestos**: Supuestos explícitos que Planner debe validar o descartar.
15. **Handoff para Planner**: Resumen funcional para la fase SDD, con decisiones pendientes.

## Reglas de Proceso
- **Claridad sobre Solución**: El enfoque es funcional; no debe definir contratos OpenAPI ni esquemas de base de datos finales (esto es labor del Planner).
- **Reducción de Ambigüedad**: Si un término es vago, se debe preguntar al usuario antes de cerrar el brief.
- **Estado de Bloqueo**: No se puede pasar a la fase `planner` si hay preguntas críticas abiertas en el brief.
- **No Diseño Prematuro**: No escribir endpoints, payloads definitivos, tablas, migraciones, clases, componentes, workflows n8n finales, task boards ni código.
- **Preguntas de Alto Impacto**: Priorizar preguntas que cambian alcance, permisos, flujo de negocio, integraciones, cumplimiento, datos sensibles, auditoría, volumen o criterios de aceptación.
- **Preguntas No Bloqueantes**: Si una duda no bloquea Planner, registrarla como pregunta abierta no crítica y continuar.
- **Trazabilidad**: Cada requisito debe poder mapearse a uno o más criterios de aceptación.

## Criterios de Calidad del Brief
- Cada funcionalidad debe tener actor, disparador, resultado esperado y casos alternos relevantes.
- Los permisos deben indicar qué rol puede hacer qué, sin diseñar todavía claims, scopes o realm config.
- Las entidades funcionales deben describir datos de negocio, no esquemas de DB.
- Las integraciones deben indicar sistema externo, propósito, dirección del flujo y criticidad, no implementación final.
- Seguridad debe cubrir acceso, datos sensibles, auditoría y abuso esperado a nivel funcional.
- Edge cases deben incluir errores de usuario, datos incompletos, duplicados, permisos insuficientes, integraciones caídas y concurrencia funcional cuando aplique.
- Criterios de aceptación deben ser verificables por usuario o test, evitando frases vagas como "funciona correctamente".

## Estados Permitidos
- `requirements-discovery`: el brief está en levantamiento.
- `requirements-blocked`: hay preguntas críticas que impiden handoff a Planner.
- `ready-for-planner`: el brief tiene suficiente claridad funcional para que Planner produzca specs SDD.

No usar `validated-not-executed`, `ready`, `todo`, `in_progress`, `done` ni `blocked` como estado del requirements brief; esos estados pertenecen a otros artefactos SDD/task boards.

## Handoff para Planner
El handoff debe incluir:
- Objetivo funcional resumido.
- Scope y out of scope.
- Actores, permisos y restricciones funcionales.
- Flujos principales y alternos.
- Entidades funcionales y datos sensibles.
- Integraciones esperadas y criticidad.
- Criterios de aceptación.
- Preguntas abiertas separadas entre críticas y no críticas.
- Supuestos explícitos.
- Riesgos funcionales que Planner debe resolver técnicamente.
