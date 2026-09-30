# Runbook: Evaluaciones de agentes (EvalOps)

Las evals son la red de seguridad del repo: cada cambio de modelo, prompt o
workflow se certifica contra casos semilla antes de instalarse. Sin evals en
verde no hay sync.

## Suites actuales (`evals/cases/`)

| Suite | Agente | Qué prueba |
|---|---|---|
| `spec-validator.yaml` | spec-validator | Aprueba la spec completa y autocontenida; rechaza incompletas, ambiguas y presión para aprobar |
| `task-decomposer.yaml` | task-decomposer | Exige Gate 1 firmado; produce el board en `todo` |
| `executor-guardrails.yaml` | executor | Bloqueos (OpenAPI, alcance, tests de test-architect) y self-healing |
| `planner.yaml` | planner | No entrega a ejecución sin spec aprobada |
| `master-orchestrator.yaml` | master-orchestrator | Cura contexto antes de planificar amplio |
| `context-curator.yaml` | context-curator | Declara fuentes incompletas/conflictivas, no inventa |
| `security-reviewer.yaml` | security-reviewer | Severidades: secreto→critical, SQLi→high+, PII en logs→medium+ |
| `ui-executor.yaml` | ui-executor | Bloquea sin dirección aprobada o ante backend; planea gauntlet |
| `final-validation.yaml` | final-validation | `not ready` ante secretos o cobertura <85%; `ready` con cadena en verde |
| `odd-*.yaml` (4) | orchestrator, executor, reviewer, bug-diagnostician | Carriles ODD: clasificación, escalamiento a SDD, boundaries, RCA |
| `quality-conditional.yaml` | master-orchestrator | Fase 6 condicional (reviewer siempre, security ante superficie sensible) |

## Ejecución

```bash
# Formato (sin modelo: no llama a ningún LLM)
python3 evals/run.py evals/cases/<suite>.yaml

# Con modelos reales (usa el binding del perfil salvo --model)
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode --model <id>
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode --repeat 2
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode --repeat 3 --threshold 0.66
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode --timeout 1200 --show-output
```

- `--repeat N`: los LLM no son deterministas; por defecto gana la mayoría.
- `--timeout`: segundos por caso (default 900). El razonamiento pesado
  (Opus 5.5 explorando el repo) puede necesitar más; si expira de forma
  sistemática, primero prueba el caso a mano antes de culpar al modelo.
- `--show-output`: imprime la respuesta del agente en los casos FAIL.
- Cada caso corre en un **sandbox temporal** (`opencode run --dir`): las
  evals nunca escriben artefactos en este repo.

## Cómo añadir un caso

1. Elige la suite del agente o crea `evals/cases/<agente-o-tema>.yaml`
   con `version`, `agent`, `system_context` (prompt mínimo, no el prompt
   completo) y `cases:` con `id`, `description`, `input` y
   `expect_contains` o `expect_regex` (`expect_not_regex` opcional).
2. **Casos autocontenidos**: todo lo que el agente necesita va inline en
   `input` (no hay repo en el sandbox). Un caso "positivo" con huecos
   reales será rechazado con razón — eso es un bug del caso, no del modelo.
3. **Prohibido secretos reales**: gitleaks corre en el pre-commit también
   sobre `evals/`. Las credenciales de prueba son placeholders obvios
   (`PON_AQUI_TU_CLAVE`, nunca claves con formato válido).
4. Para `expect_not_regex`: pide en `system_context` un formato
   máquina-legible (lista `- <agente>`, veredicto en línea exacta); si no,
   el agente "menciona para excluir" y el NOT matcha igual.
5. Valida formato (`--executor echo`, default) y luego con el modelo
   asignado antes de commitear.

## Interpretar resultados

- Un FAIL aislado con PASS al repetir = ruido del modelo, no regresión.
  Usa `--repeat 2` o `3` en suites de agentes de razonamiento caro.
- Un FAIL estable en un caso nuevo: revisa primero el caso (¿tiene huecos?,
  ¿el expect es exacto?) y la salida con `--show-output` antes de tocar
  prompts o modelos.
- Un FAIL estable tras un cambio de modelo = el modelo no es apto para el
  rol (o el rol necesita un prompt más explícito). Registra el resultado en
  el commit y elige otro candidato.
