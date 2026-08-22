---
name: code-review-checklist
description: Lista de verificación para revisión de código orientada a bugs, regresiones, drift arquitectónico, seguridad, performance, tests y cumplimiento de specs.
---

# Code Review Checklist

Esta lista de verificación define los estándares mínimos para revisar código después de implementación. La revisión debe priorizar defectos reales, regresiones, incumplimiento de specs y riesgos productivos sobre preferencias cosméticas.

## Principios de Revisión
- Findings primero, ordenados por severidad.
- Revisar contra la spec aprobada, task board, OpenAPI, migraciones y criterios de aceptación; no contra gustos personales.
- Si no hay findings, decirlo explícitamente y mencionar riesgos residuales o evidencia faltante.
- Cada finding debe incluir archivo/línea cuando sea posible, impacto, causa y remediación concreta.
- No aprobar cambios que requieren que Executor invente comportamiento no especificado.

## Severidades
- `blocker`: no se puede continuar; hay bug probable, regresión contra spec, riesgo de datos, seguridad, contrato roto o falta una decisión.
- `high`: issue serio con impacto probable en producción, seguridad, consistencia, performance o mantenibilidad crítica.
- `medium`: riesgo importante o deuda concreta que puede causar bugs o dificultar cambios próximos.
- `low`: claridad, consistencia o mejora menor sin impacto funcional inmediato.

## Checklist SDD / Contratos
- La implementación cumple la spec aprobada y no inventa comportamiento.
- No rompe Master Spec, Delta Spec, shared context ni task board.
- OpenAPI, handlers/controllers, clientes y tests usan los mismos paths, status codes, headers, schemas y error shape.
- Migraciones, entidades, queries y repositorios coinciden en nombres, tipos, nullability, índices y constraints.
- Si hay cambios posteriores a `verdict: ready`, deben volver a Spec Validator.
- No hay `Known Technical Debt`, `fix later` o deferrals no aprobados para inconsistencias de contrato.

## Checklist Funcional
- Happy path y failure paths cumplen criterios de aceptación.
- Validaciones de entrada son completas y producen errores consistentes.
- No hay cambios invisibles de comportamiento, defaults, ordenamiento, paginación, filtros o permisos.
- Edge cases relevantes están manejados: duplicados, nulos, límites, concurrencia, permisos insuficientes, integraciones caídas.

## Checklist Arquitectura / Mantenibilidad
- Respeta arquitectura hexagonal: dominio sin dependencias de infraestructura/framework.
- Use cases no delegan decisiones de negocio a controllers, repositories, UI o workflows externos.
- Boundaries entre controller/service/use case/repository/adapter son claros.
- Naming usa Ubiquitous Language y evita términos obsoletos.
- Complejidad controlada: funciones pequeñas, guard clauses, sin nesting excesivo ni duplicación riesgosa.
- No introduce abstracciones innecesarias ni acoplamiento global.

## Checklist Seguridad
- AuthN/AuthZ y tenant/user boundary están aplicados donde corresponde.
- No hay SQL/NoSQL injection, XSS, SSRF, path traversal, unsafe redirects ni shell injection.
- No se exponen secretos, tokens, PII o datos sensibles en código, logs, errores, frontend bundles o workflows.
- Errores no filtran detalles internos.
- Inputs externos se validan y outputs sensibles se filtran/encodan.

## Checklist Datos / Transacciones / Performance
- Transacciones cubren el boundary correcto y no envuelven llamadas externas lentas salvo decisión explícita.
- No hay N+1 queries, lecturas sin límite, falta de paginación, locks innecesarios o queries no indexadas en rutas críticas.
- Migraciones son forward-only, reversibles operacionalmente cuando aplique y compatibles con datos existentes.
- Idempotencia, retries y timeouts están definidos para integraciones y jobs.
- Rutas de alto volumen tienen backpressure, límites o estrategia de escalabilidad.

## Checklist Tests y Evidencia
- Cambios de comportamiento tienen tests nuevos o actualizados.
- Bugs corregidos tienen regression tests cuando sea viable.
- Coverage por archivo testable cumple `testing-strategy` o se reporta blocker.
- `pre-flight-check` fue ejecutado o marcado `skipped-with-reason` con justificación válida.
- No se agregan tests frágiles, sleeps arbitrarios ni snapshots vacíos para subir cobertura.

## Checklist Por Stack
- **Spring Boot/Java/Kotlin**: validation annotations, exception mapping, transaction boundaries, DTO/entity separation, MapStruct/Lombok/Kotlin idioms según stack, nullability y coroutine/threading si aplica.
- **SQL/NoSQL**: índices, constraints, migrations, query shape, consistencia, paginación y retención.
- **React/Angular**: state ownership, API client usage, loading/empty/error/success states, forms, accessibility, route guards y component boundaries.
- **n8n/Integraciones**: payload contract, retries, idempotencia, error handling, observability y manejo de secretos.

## Output Esperado
- Findings ordenados por severidad.
- Cada finding con archivo/línea, impacto y remediación.
- Sección de preguntas abiertas si falta contexto.
- Resumen de evidencia revisada: specs, archivos, tests/comandos si se ejecutaron.
- Si no hay findings: declarar "No findings" y listar riesgos residuales o verificaciones no ejecutadas.
