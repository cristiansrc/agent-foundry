---
name: planning-context-pack
description: Prepara un contexto de planificación persistente, mínimo y trazable desde specs y código para que un modelo de razonamiento no relea el repositorio completo.
---

# Planning Context Pack

Usa esta skill antes de planificación o discovery que requiera leer más de tres
archivos, o cuando el contexto SDD activo no permita identificar con precisión
las fuentes canónicas. No la uses para una consulta puntual ya delimitada.

## Propósito y propiedad

El `context-curator` es dueño de crear o actualizar
`docs/specs/.working/<increment-name>-planning-context.md`. El pack reduce
lecturas repetidas; no reemplaza ninguna spec, contrato ni código canónico.
El Planner lo consume como índice y verifica la fuente exacta antes de cambiar
una decisión o contrato.

## Recolección

1. Delimita el incremento y la pregunta de planificación. Busca solo en el
   repositorio activo y en las rutas canónicas de `context-pinning`.
2. Lee la master/delta spec vigente, shared context, contrato OpenAPI,
   migraciones, código y tests solo cuando sean relevantes al objetivo. Si hay
   Graphify, incluye su subgrafo o reporta que no está disponible.
3. Conserva discrepancias y evidencia. Una omisión incierta debe aparecer como
   pregunta abierta, nunca convertirse en una inferencia presentada como hecho.

## Formato obligatorio

El pack debe incluir, en este orden:

```markdown
# Planning Context Pack: <increment-name>

- generated_at: <ISO-8601>
- source_snapshot: <hash git si está disponible; si no, `unavailable`>
- pack_status: complete | incomplete | conflicting
- refresh_when: <archivos o eventos que lo invalidan>

## Objective and scope
## Canonical sources
## Existing behavior and contracts
## Decisions locked
## Impact map
## Risks and edge cases
## Conflicts and open questions
## Planner handoff
```

Cada hecho material en las secciones centrales debe terminar con evidencia en
el formato ``[ruta: sección o líneas]``. `Canonical sources` distingue fuente,
rol y razón de autoridad. `Planner handoff` lista qué puede decidir el Planner,
qué debe verificar directamente y qué bloquea el incremento.

## Límites de calidad y coste

- Incluye datos necesarios para decidir, no transcripciones ni historia stale.
- Para archivos grandes, extrae solo las secciones que responden al objetivo;
  deja ruta y rango para lectura dirigida posterior.
- Mantén el pack por debajo de 250 líneas salvo que enumerar contratos o
  conflictos requiera más. Si excede ese límite, divide por dominio y añade un
  índice, sin eliminar evidencia.
- Reutiliza el pack mientras `refresh_when` no ocurra. Si cambian fuentes
  canónicas, actualízalo antes de planificar de nuevo.
- Un `pack_status: incomplete` o `conflicting` prohíbe asumir completitud:
  el Planner debe verificar la fuente señalada o solicitar una nueva curación.
