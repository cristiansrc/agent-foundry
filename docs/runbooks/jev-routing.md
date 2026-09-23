# Runbook: routing dinámico con Jev

## Estado

Implementación inicial preparada y generada. El proveedor activo por defecto es
Vercel AI Gateway. La activación en la instalación local de OpenCode requiere
configurar la credencial y ejecutar `tooling/sync.sh`; ese último paso no forma
parte del build.

## Objetivo

Jev decide únicamente qué agente autorizado recibe la siguiente tarea, qué
nivel de razonamiento necesita (`low`, `medium`, `high`, `critical`) y si hace
falta una aclaración humana. No mantiene el contexto global, no lee las fuentes
de verdad por sí mismo, no ejecuta herramientas y no concede permisos.

`master-orchestrator` mantiene el contexto y Agent Foundry conserva la autoridad
sobre gates, permisos, agentes válidos y modelos concretos.

## Agentes con routing dinámico

La selección de Jev está limitada a:

- `planner`
- `solution-architect`
- `enterprise-architect`
- `bug-diagnostician`
- `security-reviewer`
- `final-validation`

`master-orchestrator` usa siempre el binding de Luna. Los demás agentes
mantienen su routing estático porque reciben tareas suficientemente acotadas por
las specs y el task board.

## Niveles de razonamiento

| Nivel | Modelo ChatGPT OAuth |
|---|---|
| `low` | Luna |
| `medium` | Terra |
| `high` | Sol |
| `critical` | Sol |

La traducción se genera desde `profiles/jev.yaml` y `profiles/models.yaml`.
Jev nunca devuelve ni selecciona directamente un `provider/model-id`.

## Proveedores

### Vercel AI Gateway — activo

```bash
export FOUNDRY_JEV_PROVIDER=vercel
export AI_GATEWAY_API_KEY="..."
```

Usa `POST https://ai-gateway.vercel.sh/v1/evaluate` con el modelo
`typesafe-ai/jev`. Vercel utiliza `boolean` para la pregunta binaria.

### Jev oficial — alternativo

```bash
export FOUNDRY_JEV_PROVIDER=typesafe
export JEV_API_KEY="..."
```

Usa `POST https://thejevai.com/v1/systemone` con `jev-latest`. La API oficial
usa `noul` para la pregunta binaria. La conversión se realiza en el adapter.

Las claves viven solamente en el entorno local del proceso. Nunca deben entrar
en `profiles/`, skills, prompts, logs o commits.

## Contexto enviado

El estado enviado a Jev debe incluir únicamente:

- tarea actual y fase SDD;
- estado del incremento, veredicto y firmas de gate;
- candidatos autorizados, propósito y límites;
- artefactos relevantes por ruta, sin volcar su contenido completo;
- findings, blockers y preguntas abiertas;
- restricciones de permisos y política de routing.

No se deben enviar Master Specs completas, código, logs extensos, secretos ni
la conversación completa. `context-curator` o `master-orchestrator` preparan el
contexto mínimo.

## Preguntas y confianza

La consulta estándar contiene tres preguntas paralelas:

- `next_agent`: elección entre agentes permitidos;
- `reasoning_level`: elección entre los cuatro niveles;
- `needs_human_clarification`: decisión binaria.

Se usan las probabilidades y la confianza nativas de Jev. No se pregunta
adicionalmente “¿qué tan seguro estás?” porque Choice y Score ya devuelven
confianza. Para `noul`/`boolean` se usa la probabilidad de la respuesta.

```text
>= 0.80  routing automático
0.60-0.79 confirmación humana
< 0.60   aclaración humana obligatoria
```

Una recomendación de Jev nunca puede saltar un gate, alterar un permiso ni
seleccionar un agente fuera de la matriz.

## Gate 1 y reentrada de Planner

Después de `## Human Plan Approval: approved_by_user`:

- si la spec no cambió y no hay decisión pendiente, se enruta a
  `task-decomposer`;
- si la aprobación introduce cambios, conflicto o una decisión técnica,
  arquitectónica o funcional, se reactiva `planner`;
- si solo hay que normalizar metadata o estado, se prefiere una transición
  determinista del orquestador/plugin, sin invocar Planner.

## Bugs e inconsistencias

`bug-diagnostician` permanece en modo solo lectura y clasifica el caso antes de
enrutarlo:

| Clasificación | Ruta esperada |
|---|---|
| `mechanical` | `executor` o `spec-remediator` |
| `technical-decision` | `planner` |
| `architectural-decision` | `planner` o `solution-architect` |
| `functional-decision` | `planner` |
| `environment` | `devops-architect` |
| `user-decision-required` | bloqueo y consulta humana |

Jev puede recomendar la ruta y el nivel dentro de candidatos válidos, pero la
clasificación determinista y la independencia de validadores prevalecen.

## Archivos de implementación

| Archivo | Responsabilidad |
|---|---|
| `profiles/jev.yaml` | Proveedores, modelo, umbrales y bindings |
| `core/skills/jev-routing/SKILL.md` | Contrato para los agentes |
| `plugins/opencode/jev-mcp/server.py` | MCP local y adapters HTTP |
| `plugins/opencode/jev-mcp/README.md` | Configuración y credenciales |
| `plugins/opencode/model-router/model-router.ts.tmpl` | Consulta Jev y aplicación del modelo |
| `adapters/shared/render.py` | Configuración generada del plugin |
| `core/workflow/matrix.yaml` | Agentes habilitados para la skill |
| `core/agents/sdlc/consultants/master-orchestrator.md` | Contexto y Gate 1 |

## Build, activación y rollback

```bash
./tooling/lint.sh
./tooling/build.sh
export AI_GATEWAY_API_KEY="..."
echo y | ./tooling/sync.sh
```

Reinicia OpenCode después del sync. Para volver al comportamiento anterior,
desactiva el MCP o elimina la credencial: el plugin conserva el routing
estático cuando Jev no está disponible.

## Verificación realizada

- `tooling/lint.sh`: correcto.
- `tooling/build.sh`: correcto.
- MCP `initialize`: correcto.
- MCP `tools/list`: correcto.
- MCP sin credencial: falla explícitamente y no expone secretos.
- Llamada real a Vercel: pendiente de ejecutar con `AI_GATEWAY_API_KEY` local.
