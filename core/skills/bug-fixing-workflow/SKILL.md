---
name: bug-fixing-workflow
description: Protocolo riguroso para la resolución de errores. Prioriza la reproducción empírica y la integridad arquitectónica sobre los parches rápidos.
---

# Bug Fixing Workflow

Esta skill define cómo los agentes deben abordar fallos reales o sospechados en el sistema. El objetivo es corregir la causa raíz con el cambio mínimo seguro, proteger el comportamiento con regression tests y evitar cambios colaterales no solicitados.

## 1. Triage Inicial
Antes de modificar código, clasificar el caso:
- `confirmed-bug`: el comportamiento actual contradice spec, contrato, test existente o intención explícita del usuario.
- `suspected-bug`: hay síntomas, pero falta reproducción o evidencia.
- `requirements-change`: el comportamiento actual coincide con la spec, pero el usuario quiere cambiarlo.
- `environment-issue`: falla por configuración, servicios, datos locales, permisos, red o entorno.
- `test-bug`: el test está mal o quedó obsoleto frente a una spec vigente.

Si es `requirements-change`, no aplicar fix directo: crear o solicitar Delta Spec mediante Planner.

## 2. Reproducción (Mandatorio)
Antes de proponer una solución, el agente debe intentar reproducir el bug:
1. Ejecutar el comando, flujo o test que demuestra el fallo.
2. Registrar input, pasos, resultado actual, resultado esperado y evidencia del error.
3. Crear o actualizar un test unitario, integración, API, UI o workflow que falle por el bug cuando sea viable.
4. Si no se puede crear test automatizado, documentar una reproducción manual verificable y explicar por qué no es automatizable.
5. Identificar el estado actual vs. comportamiento esperado definido por Master Spec, Delta Spec, OpenAPI, migraciones, task board o solicitud explícita del usuario.

No reportar bug como corregido si nunca se reprodujo ni se explicó por qué la reproducción no fue posible.

## 3. Diagnóstico y Raíz (Root Cause)
- El agente debe explicar POR QUÉ ocurrió el fallo.
- ¿Es una violación de la arquitectura hexagonal? ¿Es un edge case no cubierto en la spec inicial? ¿Es un drift entre el código y el contrato OpenAPI?
- Separar síntoma de causa raíz.
- Identificar el primer commit/cambio/artefacto sospechoso si hay evidencia local disponible.
- Verificar si el fallo viene de código, spec, datos, migración, integración, configuración o test.

## 4. Estrategia de Solución
- **Alineación:** La solución debe respetar la separación de capas (Dominio, Aplicación, Infraestructura).
- **No Side-Effects:** Evaluar si el fix afecta a otras partes del sistema.
- **SDD Integration:** Si el fix cambia una regla de negocio, el agente debe crear una `Delta Spec` de corrección.
- **Fix Mínimo:** Cambiar solo lo necesario para corregir la causa raíz.
- **Sin Refactor Mezclado:** No mezclar refactors, mejoras cosméticas, upgrades o features en un bug fix salvo que sean indispensables para corregir el bug.
- **Compatibilidad de Contratos:** Si el fix requiere cambiar OpenAPI, migraciones, auth rules, payloads, workflow externo o comportamiento visible, detener y enrutar a Planner/Spec Validator.
- **Datos Existentes:** Si el bug afecta persistencia o migraciones, evaluar impacto en datos existentes y compatibilidad operacional.

## 5. Regression Tests
- Todo bug corregido debe incluir regression test que falle antes del fix y pase después, cuando sea viable.
- Si no se agrega regression test, debe existir justificación explícita (`skipped-with-reason`) y verificación manual reproducible.
- El test debe cubrir la causa raíz, no solo el síntoma superficial.
- No usar tests frágiles, sleeps arbitrarios ni asserts débiles solo para demostrar cobertura.

## 6. Validación Final
- El test de reproducción debe pasar.
- Se deben ejecutar tests de regresión de la zona afectada.
- Ejecutar `pre-flight-check` aplicable y reportar comandos/resultados.
- Si aplica cobertura, cumplir `testing-strategy` para archivos testables afectados.
- Si una falla preexistente no relacionada impide validar, reportar `pre-existing failure` con evidencia y separar el riesgo del fix.

## 7. Criterios de Bloqueo
Bloquear el bug fix cuando:
- No existe comportamiento esperado autoritativo y el agente tendría que inventarlo.
- El fix requiere cambiar contrato, schema, autorización, transacción o integración sin spec aprobada.
- No se puede reproducir ni explicar razonablemente el fallo.
- La corrección rompe tests existentes o introduce regresiones.
- El bug implica riesgo de seguridad o datos y requiere revisión especializada.

## 8. Reporte Esperado
El cierre del bug fix debe incluir:
- Clasificación del triage.
- Pasos de reproducción.
- Root cause.
- Fix aplicado y archivos cambiados.
- Regression test agregado o justificación de omisión.
- Comandos de validación ejecutados y resultados.
- Riesgos residuales.
- Indicación de si requiere Reviewer, Security Reviewer o Planner.
