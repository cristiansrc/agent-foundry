---
name: documentation-lifecycle
description: Gestión del ciclo de vida de la documentación técnica. Automatiza la consolidación de incrementos en la Master Spec para mantener una fuente de verdad única.
---

# Documentation Lifecycle

Esta skill asegura que la documentación del proyecto no se degrade con el tiempo.

## 1. Gestión de Master Spec
La `Master Spec` (ubicada en `docs/specs/master_spec.md`) representa la verdad actual del sistema.

## 2. Flujo de Consolidación
Tras la aprobación de un incremento (Delta Spec):
1. El agente de `documentation` debe integrar los cambios del incremento en la `Master Spec`.
2. Se deben eliminar las secciones obsoletas y actualizar diagramas Mermaid si es necesario.
3. El incremento se mueve a una carpeta de historial (`docs/specs/archive/`) o se mantiene como referencia inmutable.

## 3. Sincronización con OpenAPI
- Cualquier cambio en la documentación que afecte contratos debe verse reflejado en la ruta OpenAPI canonica declarada por el proyecto.
- El agente debe validar que las descripciones en el YAML coincidan con las reglas de negocio descritas en la Master Spec.
- Documentation no debe editar OpenAPI; si detecta drift contractual debe reportarlo para Planner.

## 4. Trazabilidad
Cada cambio estructural en el código debe poder rastrearse hasta una sección de la Master Spec o un ID de incremento.
