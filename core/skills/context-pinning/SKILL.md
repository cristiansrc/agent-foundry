---
name: context-pinning
description: Gestión de archivos críticos para mantener la integridad arquitectónica y el diseño del sistema. Asegura que los agentes siempre lean la Master Spec y los contratos vigentes.
---

# Context Pinning Skill

Esta skill asegura que los agentes siempre trabajen sobre la base de conocimiento actualizada del proyecto.

## 1. Archivos Core en `.opencode-context`
El agente debe priorizar la lectura de:
- **Master Spec de Solución:** Si existe una carpeta `proyectos/` en el nivel superior, leer la spec macro en `../../docs/specs/master_spec.md`.
- **Master Spec del Proyecto:** `docs/specs/master_spec.md` (Fuente de verdad funcional consolidada del microservicio).
- **Contratos OpenAPI:** ruta canonica declarada por el proyecto en shared context o spec. Para Spring Boot, ubicaciones validas por defecto: `docs/api/openapi.yaml`, `docs/api/openapi.yml`, `src/main/resources/openapi.yaml` o `src/main/resources/openapi.yml`.
- **Reporte de Dependencias Graphify:** `graphify-out/GRAPH_REPORT.md` (si el proyecto tiene Graphify configurado).
- **Memoria del Proyecto/Workspace:** `MEMORY.md` (registro histórico de lecciones aprendidas y decisiones de diseño complejas que no deben reincidir).


- **Incrementos Activos:** Cualquier spec en `docs/specs/increments/` que aún no haya sido consolidada.
- **Configuración Gradle:** `build.gradle` y `settings.gradle`.
- **Contexto SDD activo:** `docs/specs/.working/<increment>-sdd-context.md`.
- **Task board activo:** `docs/specs/tasks/<increment>-task-board.md` cuando exista.

## 2. Regla de Análisis de Cambio
Antes de modificar código, el agente DEBE:
1. Validar la tarea contra la `Master Spec` para entender el impacto global.
2. Si es una modificación, identificar la spec de incremento que originó la lógica actual para no romper reglas históricas.
3. Si Graphify está activo, revisar `graphify-out/GRAPH_REPORT.md` (o usar `graphify query`) para evaluar dependencias funcionales y estructurales antes de realizar modificaciones.

## 3. Prevención de Drift
El agente debe alertar si detecta que el código que va a modificar no coincide con lo descrito en el contexto "pineado".

No se debe asumir una ruta unica de OpenAPI si el shared context declara otra ruta canonica existente. La ruta declarada debe verificarse leyendo el archivo real antes de marcar consistencia.
