---
name: outcome-observability-driven
description: Carriles ligeros trivial y fix que complementan SDD — Outcome-Driven (resultado verificable) + Observability-Driven (reproducción y señales) con odd-card de una página, límites explícitos y escalamiento obligatorio a SDD ante cualquier decisión de negocio o arquitectura.
---

# Outcome + Observability Driven Development (ODD)

ODD **no reemplaza** a Spec-Driven Development. Es el camino corto para
cambios donde las decisiones de negocio y arquitectura ya están tomadas o no
existen. SDD sigue siendo el único camino para decidir.

- **Outcome-Driven:** se define QUÉ debe ser verdad al terminar y CÓMO se
  demuestra, sin spec completa.
- **Observability-Driven:** antes de corregir, se reproduce con evidencia
  (test o señal que falla) y se declara la señal (log/métrica/traza) que
  confirma el comportamiento en ejecución.

## 1. Carriles

| Carril | Aplica a | Flujo | Aprobaciones para merge |
|---|---|---|---|
| `trivial` | docs, config sin efecto en runtime, renombres locales, typos | odd-card mínima → executor → reviewer → git-executor | reviewer |
| `fix` | bug con alcance acotado y comportamiento esperado ya definido (spec, contrato, test o intención explícita) | bug-diagnostician → odd-card → executor → reviewer → Gate 2 → git-executor | reviewer **y** humano (Gate 2) |
| `feature` | nuevo comportamiento, incremento | SDD completo (lifecycle §3) | Gate 1 + Gate 2 |
| `workspace` | cambios que cruzan servicios | SDD + enterprise | Gate 1 + Gate 2 |

Reglas de clasificación:
1. Clasifica el `master-orchestrator` al inicio y lo declara en el shared
   context como `## Lane: <carril>`.
2. El humano puede **subir** el carril; ningún agente puede **bajarlo**.
3. Ante duda entre dos carriles, se elige el más alto.

## 2. Disparadores de escalamiento a SDD (obligatorios)

Si durante diagnóstico, ejecución o revisión aparece cualquiera de estos, el
trabajo se detiene con `Blocked: escalate-to-sdd` y el estado pasa a
`escalated-to-sdd` (el incremento reinicia en `planning` como `feature`):

- Cambio en contratos OpenAPI/AsyncAPI, eventos o payloads públicos.
- Cambio en esquema de BD o migraciones.
- Cambio en autenticación, autorización, roles o permisos.
- Módulo, servicio, dependencia o integración externa nueva.
- Decisión de negocio: el comportamiento esperado no está definido en spec,
  contrato, test existente o petición explícita del usuario
  (`requirements-change` en `bug-fixing-workflow`).
- El diff previsto supera los `boundaries` declarados en la odd-card.

Escalar no es un fallo: es el guardarraíl que evita que ODD sea un atajo
para saltarse SDD.

## 3. Plantilla odd-card

Ruta: `docs/specs/odd/<nombre>.md` (Placeholder Guard: nombre real).

```markdown
# ODD: <nombre>
lane: fix | trivial
origin: <issue / reporte / RCA path>

## Outcome
<qué debe ser verdad al terminar, 1-3 líneas, observable y verificable>

## Evidence
- before: <comando/test/señal que FALLA hoy + resultado observado>
- after:  <el MISMO comando/test/señal en VERDE>

## Signals            (obligatorio en fix; opcional en trivial)
- <log/métrica/traza que confirma el comportamiento en ejecución>

## Boundaries
- touches: <archivos o módulos permitidos>
- must-not-touch: contratos, esquema BD, auth + <otros>

## Escalation
<vacío, o disparador §2 que obligó a escalar>
```

En `trivial`, `before` puede ser la observación del estado actual (p. ej.
el typo en la línea X) y `after` el check que lo confirma (lint, build,
render de docs).

## 4. Protocolo del carril fix

1. **Diagnóstico (bug-diagnostician):** triage según `bug-fixing-workflow`
   §1. Si no es `confirmed-bug` → no hay carril fix (`requirements-change`
   escala a SDD; `environment-issue` va a devops-architect).
2. **Reproducción observable:** test automatizado que falla y, si el fallo
   es de runtime, la señal existente que lo evidencia. Si la señal no
   existe, la odd-card la declara como parte del outcome (instrumentar es
   parte del fix, dentro de boundaries).
3. **odd-card:** `documentation` la transcribe desde el RCA sin añadir
   decisiones propias.
4. **Ejecución (executor):** primero confirma que `before` falla; implementa
   el cambio mínimo dentro de `boundaries`; confirma `after` en verde y la
   suite existente sin regresiones. Máximo 3 intentos (self-healing).
5. **Revisión (reviewer):** diff dentro de boundaries, evidencia
   before/after real, sin disparadores de escalamiento, test de regresión
   presente. Emite `review: approved` o `review: changes-requested`.
6. **Gate 2 humano** y luego git-executor.

## 5. Criterios de cierre

- [ ] Evidencia `before` registrada (falló) y `after` verde, mismo comando.
- [ ] Test de regresión nuevo o existente que cubre el caso.
- [ ] Señal declarada presente (fix).
- [ ] Diff dentro de boundaries; ningún disparador §2.
- [ ] `## Reviewer Approval: approved` transcrito en el shared context.
- [ ] Carril fix: `## Human QA Approval: approved_by_user`.

## 6. Anti-patrones

- Usar `fix` para comportamiento nuevo "pequeño" → es `feature`.
- Escribir el test después del fix sin haberlo visto fallar.
- Ampliar boundaries a mitad de ejecución en vez de escalar.
- Declarar señales que no existen ni se implementan.
- Cerrar un fix con "funciona en mi máquina" como evidencia.
