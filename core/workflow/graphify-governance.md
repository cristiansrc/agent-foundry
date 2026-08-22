# Gobernanza de Grafos de Conocimiento (Graphify)

Estándar para mantener `graphify-out/` sincronizado en los repositorios activos.
Portado desde config-ai (graphify_governance_standard.md) al ecosistema foundry.

## Principios

1. **El grafo es cache derivado, nunca fuente de verdad**: specs, código y
   contratos mandan; si el grafo contradice al repo, se regenera el grafo.
2. **Actualización incremental obligatoria** tras cambios de código relevantes:
   los agentes obreros ejecutan `graphify update .` antes de reportar done.
3. **Consulta antes que grep**: para preguntas de arquitectura/relaciones,
   `graphify query "<pregunta>"` primero; GRAPH_REPORT.md solo para revisión
   amplia inicial.

## Cuándo actualizar

| Evento | Acción |
|--------|--------|
| Fin de implementación del task board (executor) | `graphify --update` incremental obligatorio |
| Refactors estructurales (refactor) | `graphify update .` + verificar nodos movidos |
| Inicialización de repo | `graphify install --project` + `graphify update .` |
| Workspace multi-repo | install/update en la RAÍZ de la solución |

## Reglas de commit

- Los archivos actualizados del grafo (`graphify-out/graph.json`,
  `GRAPH_REPORT.md`) van al index cuando el commit modifica código fuente.
- Excluir del grafo: HTML pesados, imágenes, configs locales del entorno.
- Archivos sucios en graphify-out/ tras hooks son esperados; NO son razón para
  saltarse graphify — solo lo es una tarea sobre salida stale o incorrecta.

## Anti-patrones

- Regenerar el grafo completo por rutina (costoso): preferir incremental.
- Editar archivos de graphify-out/ a mano.
- Usar el grafo como justificación para no leer la spec real.
