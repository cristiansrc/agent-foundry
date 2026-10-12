---
name: workspace-coordination
description: Coordinación técnica ascendente y descendente entre el Solution Workspace y proyectos locales, incluyendo la gestión y visibilidad de la deuda técnica.
---

# Workspace Coordination and Technical Debt Skill

Esta skill define el protocolo técnico para coordinar las especificaciones y contratos de integración en un entorno de múltiples servicios (Solution Workspace), usando Graphify y un sistema estructurado de registro de deuda técnica.

## 1. Flujo de Coordinación

### A. Sincronización Ascendente (Proyecto -> Workspace)
* Al finalizar desarrollo/validación de proyecto local según mapping autorizado:
  1. El `planner` local debe consolidar la especificación y los contratos OpenAPI.
  2. El `enterprise-architect` debe invocar la actualización de dependencias e interfaces del workspace.
   3. Worker con shell actualiza Graphify sólo por cambio estructural/material; cache no es gate normativo.

### B. Sincronización Descendente (Workspace -> Proyecto)
* El `enterprise-architect` documenta los cambios arquitectónicos globales en `docs/specs/workspace_changes.md`.
* Agentes locales leen workspace_changes y fuentes afectadas declaradas. Grafo sólo para relaciones relevantes, sin re-curación por transcripción de estado.
* Si el proyecto es afectado, se crea una Delta Spec local para adaptar el código a la especificación global.

## 2. Gestión de Deuda Técnica (Technical Debt)
* **Registro Local:** Cada proyecto mantiene `projects/<project-name>/docs/specs/technical_debt.md`.
* **Registro Global:** El Workspace mantiene `docs/specs/technical_debt.md`.
* **Reglas de Registro:**
  - Cualquier agente que introduzca un bypass de diseño, baja cobertura temporal o un parche rápido, debe añadir una entrada estructurada detallando ID, descripción, impacto, plan de mitigación y estado (`active`).
  - El `enterprise-architect` consolidará periódicamente los registros de deuda técnica locales en el archivo global del Workspace.
  - Al planificar, los agentes deben usar `graphify query` para identificar si hay deudas activas que bloqueen o afecten la tarea de desarrollo.
