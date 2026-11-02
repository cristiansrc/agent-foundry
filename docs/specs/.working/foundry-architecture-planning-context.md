# Planning Context Pack: foundry-architecture-docs

- generated_at: 2026-11-02T01:21:45Z
- source_snapshot: a865eb0919ca3a90fc96ba4eacbe29c14495ea79 (refs/heads/main == origin/main; sin merge en curso)
- pack_status: conflicting
- refresh_when: cambios en `profiles/*.yaml`, `core/workflow/states.md`, `tooling/gen-readme.py` o `tooling/build.sh`, avance de HEAD (nuevo commit), o resolución de las contradicciones C1-C7 de esta sección.

## Objective and scope

Carril declarado por el orquestador: **trivial** (documentación solamente, sin efecto runtime). Preparar contexto para documentar la arquitectura actual y futura de Agent Foundry (fábrica de agentes/skills agnósticos de modelo). Este pack NO implementa nada; solo indexa hechos verificables, contradicciones y el inventario de cambios preexistentes del working tree, que debe preservarse intacto.

Límites de evidencia (runtime de esta sesión): **no hay herramienta shell**, por lo que `git status`/`git diff` no pudieron ejecutarse. El inventario del working tree se derivó comparando archivos locales (lectura directa `read`/`grep`/`glob`) contra el contenido en GitHub raw del mismo SHA HEAD. Distinción staged/unstaged: no verificable. `graphify-out/` no existe → sin grafo disponible. No se leyeron credenciales, `.opencode/` ni `.venv/`.

## Canonical sources

| Fuente | Rol | Autoridad |
|---|---|---|
| `core/` (agents/skills/workflow) | Fuente de verdad agnóstica | Norma: sin `model:` ni rutas absolutas (lint la exige) `[AGENTS.md:21-22]` |
| `profiles/models.yaml`, `profiles/permissions.yaml` | Únicos bindings modelo/permisos | Autoridad máxima para modelo por agente, tier, `harness.excluded` `[AGENTS.md:23-26; profiles/permissions.yaml:8-19]` |
| `core/workflow/states.md` | Enum canónico de estados/gates/carriles | Fuente única de estados `[core/workflow/states.md:3-5,46-60]` |
| `tooling/build.sh` → `adapters/*/out/` | Salidas generadas (gitignored) | Nunca editar a mano `[AGENTS.md:16; .gitignore:1-4]` |
| `install-manifest.yaml` + `tooling/install-project.py` | Contrato de instalación por proyecto | Consumidor: instalación determinista con recibo `[install-manifest.yaml:1-35; AGENTS.md:17-20]` |
| `README.md` (bloque `BEGIN/END:GENERATED-TABLES`) | Tablas generadas por `tooling/gen-readme.py` | Derivada; no editar a mano `[README.md:206,474]` |
| `README.md` (prosa), `AGENTS.md`, `PLAN.md` | Convenciones y plan | Prosa con contradicciones puntuales (ver C1-C7) |
| `docs/runbooks/*.md` (12) | Procedimientos operativos | Autoridad por tema (evals, model-change, harness, mcps, phase2) |
| `docs/investigations/*.md` (5) | Investigación previa, no runbook | Contexto futuro, no norma `[AGENTS.md:47]` |
| `evals/run.py` + `evals/cases/*.yaml` (23 suites) | Regresión de comportamiento | Evidencia de comportamiento `[README.md:106-111]` |

ADRs: **no existen** (sin `docs/adr/`, sin archivos `*decision*`). Las decisiones viven en `PLAN.md §Decisiones tomadas` y en `docs/investigations/`.

## Existing behavior and contracts

Arquitectura actual verificada:

- Flujo de datos: `core/ → profiles/ → adapters/ → out/` `[README.md:34-49; AGENTS.md:9-12]`.
- Render opencode: `adapters/shared/render.py` itera `core/agents/**/*.md` filtrando por `harness.primary|active_subagents|optional_subagents` de `permissions.yaml`; `harness.excluded = [general, architect-executor, requirements-analyst, refactor]` → 23 agentes en `adapters/opencode/out/agents/` (27 en core) `[adapters/shared/render.py:168-198; profiles/permissions.yaml:9-19]`.
- Render kiro: `adapters/kiro/render.py` renderiza TODOS los agentes core sin filtro de exclusión `[adapters/kiro/render.py:66-77]`.
- Chatgpt (Codex): `adapters/chatgpt/out/` contiene `AGENTS.md`, `config.toml` y skills; bindings son "recomendaciones sin evals" `[README.md:410-411]`.
- Routing runtime: plugin `model-router` fuerza modelo en hook `chat.message` (Task no acepta `model`) `[plugins/opencode/model-router/README.md:8-20]`.
- Instalación: `tooling/sync.sh` es alias de `install-project.py` `[tooling/sync.sh:1-5]`; manifiesto instala agents+skills+3 plugins en `.opencode/` `[install-manifest.yaml:8-24]`.
- Puente local ChatGPT↔OpenCode: `tooling/opencode_bridge.py` (solo lectura, loopback-only), `tooling/opencode_mcp.py` (stdio MCP, 4 tools, project-scoped), `tooling/opencode_mcp_launch.py` (launcher con Secret Service) `[tooling/opencode_bridge.py:1-5,20-32; tooling/opencode_mcp.py:1-32; tooling/opencode_mcp_launch.py:1-16]`.
- Carriles: trivial/fix (ODD) no pasan por specs completas; `trivial` exige `## Reviewer Approval: approved` sin gates humanos `[core/workflow/states.md:46-60,162-163]`.
- Verificación de cierre en este repo: `./tooling/lint.sh && python3 tooling/audit_matrix.py && ./tooling/build.sh` `[AGENTS.md:83-87]`.

Contratos duros a preservar en cualquier documento futuro: anti-drift de `core/`, `profiles/` como única fuente de bindings, out/ solo por build, commit sólo si el usuario lo pide, pre-commit con lint+audit `[AGENTS.md:14-33]`.

## Decisions locked

No reabrir (registradas con fundamento en `PLAN.md:53-145` y confirmadas en fuentes actuales):

- OpenCode es el harness recomendado (único con evals ejecutadas y suscripciones combinadas) `[README.md:106-111]`.
- Reparto por forma de facturar (ChatGPT Plus razonamiento / OpenCode Go volumen) `[PLAN.md:80-99; docs/runbooks/opencode-harness.md:16-24]`.
- `fallbacks` es config muerta; no degrada en runtime `[PLAN.md:110-117]`.
- Visión: sin MCP propio; modelos con visión nativa; foundry-vision retirado 2026-09-27 `[README.md:195-202; docs/runbooks/mcps.md:28-34]`.
- Instalación por proyecto (no global), manifiesto + recibo `[AGENTS.md:17-20,49-81]`.
- Carriles ODD (trivial/fix) complementarios a SDD; architect-executor y refactor deprecados `[README.md:113-125,214,220]`.

## Impact map

Archivos relevantes para la futura documentación de arquitectura:

- Documentación a alinear: `README.md` (prosa, no el bloque generado), `AGENTS.md`, `PLAN.md`, `docs/runbooks/mcps.md`, `docs/runbooks/opencode-harness.md`, `docs/runbooks/model-router.md`, `docs/runbooks/chatgpt-opencode-phase1.md|phase2.md|phase15-results.md`, `docs/runbooks/agent-operations.md`.
- Posibles nuevos (decisión del Planner/humano): `docs/architecture.md`, `docs/adr/`, `MEMORY.md` raíz.
- Fuentes que NO se editan pero alimentan la doc: `profiles/*.yaml`, `core/**`, `tooling/gen-readme.py` (dueño de las tablas README).
- Artefactos locales a preservar sin tocar: ver inventario siguiente.

Inventario de cambios preexistentes en el working tree (detectados contra HEAD `a865eb0`; conservar intactos):

| # | Path | Estado inferido | Evidencia |
|---|---|---|---|
| 1 | `.gitignore` | modificado (+3 líneas: bloque dogfooding `.opencode/`) | local líneas 25-27 ausentes en HEAD |
| 2 | `tooling/opencode_bridge.py` | modificado (+ respaldo SQLite de sesiones: `open_history_db`, `sessions_local`, `list_sessions_result`) | `[tooling/opencode_bridge.py:256,276,342]`; local ~24.7KB vs HEAD ~14.9KB |
| 3 | `tooling/opencode_mcp.py` | modificado (`--opencode-db`, `handle(..., db=None)`, llama `bridge.list_sessions_result`) | `[tooling/opencode_mcp.py:39,79,100]` |
| 4 | `tooling/tests/test_opencode_bridge.py` | modificado (tests de respaldo `db=`) | `[tooling/tests/test_opencode_bridge.py:97,161-176]`; local ~16.5KB vs HEAD ~8.7KB |
| 5 | `tooling/tests/test_opencode_mcp.py` | modificado (mocks `list_sessions_result`, flag `--opencode-db`) | `[tooling/tests/test_opencode_mcp.py:66-105]` |
| 6 | `docs/runbooks/chatgpt-opencode-phase2.md` | modificado (+ secciones launcher/secret-tool y respaldo de historial) | `[docs/runbooks/chatgpt-opencode-phase2.md:42-104,140-164]`; local ~9.2KB vs HEAD ~4.4KB |
| 7 | `tooling/opencode_mcp_launch.py` | NUEVO sin trackear (ausente del tree remoto en HEAD) | tree GitHub HEAD sin `launch`; `[tooling/opencode_mcp_launch.py:1-16]` |
| 8 | `tooling/tests/test_opencode_mcp_launch.py` | NUEVO sin trackear | tree remoto sin ese path; `[tooling/tests/test_opencode_mcp_launch.py:1-27]` |
| 9 | `plugins/opencode/jev-mcp/__pycache__/server.cpython-314.pyc` | artefacto huérfano (source `server.py` ausente local y remoto; dir no existe en remoto) | glob local solo pycache |
| 10 | `core/skills/jev-routing/` | directorio vacío local, ausente en remoto (skill sin SKILL.md) | lectura dir = 0 entradas |
| 11 | `core/agents/installer/` | directorio vacío local, ausente en remoto | lectura dir = 0 entradas |
| 12 | `adapters/kiro/out/agents/installer.md` | artefacto generado stale (kiro render no filtra; fuente installer ya no existe) | `[adapters/kiro/render.py:72-74]` + dir core vacío |
| 13 | `d3dx9_42.log` (raíz), `.venv/`, `.playwright-mcp/`, `.opencode/`, `__pycache__/`, `adapters/*/out/` | ignorados por `.gitignore` (ruido local, no trackear) | `[.gitignore:1-27]` |

Los items 1-8 forman un cambio en curso coherente (respaldo SQLite + launcher seguro del puente MCP). No revertir, no regenerar encima, no editar como parte de esta tarea documental.

## Risks and edge cases

- README: el bloque generado se sobrescribe con `build.sh`; cualquier doc nueva debe editarse fuera del bloque o vía `gen-readme.py` `[README.md:206-474; AGENTS.md:16]`.
- Tablas generadas derivan de `core/`+`profiles/`; "arreglar" una tabla a mano revierte en el próximo build.
- Contradicciones de rol (C1): mover archivos de agente NO es carril trivial (altera render/manifest); la corrección documental debe alinearse al frontmatter+tabla generada, no mover el archivo.
- Los artefactos huérfanos (items 9-12) pueden confundir recuentos de agentes/skills; la doc debe contar desde `core/`, no desde `out/`.
- Sin shell en este runtime: no se pudo ejecutar lint/build/evals para verificar afirmaciones de ejecución; verificación queda para rol con shell.
- Límite de evidencia de codificación: `markitdown` decodificó como latin-1 algunos .md con acentos (bytes inflados); la comparación de esos archivos se hizo con `read`/`grep` directos.

## Conflicts and open questions

Contradicciones detectadas (todas documentación-vs-documentación o documentación-vs-profiles; ninguna bloquea el carril trivial, pero exigen verificar fuente antes de escribir):

- **C1** `functional-tester-agent`: archivo en `core/agents/sdlc/workers/`, prosa README lo lista como Worker `[README.md:131]`, pero frontmatter `role: validator` `[core/agents/sdlc/workers/functional-tester-agent.md:3]` y tabla generada dice Validator `[README.md:236]`. Fuente con autoridad: frontmatter+tabla generada (derivada de core).
- **C2** README prosa de visión desactualizada: `ui-designer (Claude Sonnet 5.5)` `[README.md:198-199]` vs tabla generada `openai/gpt-6-luna` `[README.md:407]` y `profiles/models.yaml:43` (slot luna; "Era Sonnet 5.5" `[profiles/models.yaml:41]`). También `functional-tester-agent (MiMo...)` `[README.md:199-200]` vs binding actual `harness_chatgpt/luna` `[profiles/models.yaml:74]`.
- **C3** `docs/runbooks/mcps.md:31-33` obsoleto: `ui-executor/functional-tester = DeepSeek Vision` (retirado 2026-10-18 `[profiles/models.yaml:445]`) y `reviewer = LongCat-2.0` (reactivado GLM-5.3 2026-10-22 `[profiles/models.yaml:55,104]`).
- **C4** `AGENTS.md:39` estructura `core/agents/{sdlc,personal}/`; real: `sdlc/` + `installer/` (vacío). No existe `personal/`.
- **C5** `PLAN.md:31` fase 4 (adapter opencode paridad 1:1) marcada ⬜, pero README/AGENTS presentan el adapter como plenamente operativo (build, install, plugins, evals) `[README.md:47-49,70-75; AGENTS.md:83-87]`. PLAN.md parece stale.
- **C6** `PLAN.md:149-152` pendientes ya implementados: enum de estados centralizado existe `[core/workflow/states.md:3-5]`; regla anti-drift en lint existe `[AGENTS.md:21-22]`; `MEMORY.md` raíz sigue ausente (solo `templates/MEMORY.md`).
- **C7** Recuentos README: índice enlaza `#skills-76` `[README.md:17]` vs encabezado `Skills (75)` `[README.md:242]` (real: 75 SKILL.md; el dir 76 `jev-routing` está vacío); y prosa dice "12 suites en evals/cases" `[README.md:107]` vs 23 archivos reales en `evals/cases/`.

Preguntas abiertas (requieren rol con autoridad, no este pack):

1. ¿Restaurar o eliminar los restos de installer/jev (items 9-12) y documentar esa decisión? Afecta recuentos y al adapter kiro.
2. ¿Crear ADRs y `docs/architecture.md` como fuentes nuevas, o consolidar en README+runbooks? Decisión de formato del Planner/humano.
3. ¿La doc futura debe reflejar el trabajo en curso del puente MCP (items 1-8) como "estado actual" o esperar a commit? Si se documenta, verificar contra los archivos locales, no contra HEAD.

## Planner handoff

- Puede decidir el Planner: estructura y ubicación de la documentación de arquitectura (README vs `docs/architecture.md` vs ADRs), alcance de corrección de C1-C7, y qué hacer con los items huérfanos (como recomendación; ejecución requiere rol autorizado).
- Debe verificar directamente antes de escribir: bindings vigentes en `profiles/models.yaml` (autoridad sobre toda prosa), estado real de `evals/cases/`, y contenido actual de `docs/runbooks/chatgpt-opencode-phase2.md` (incluye secciones no committeadas).
- Bloqueos: ninguno para carril trivial de documentación. No editar: `adapters/*/out/`, bloques `GENERATED-TABLES` de README, `profiles/`, `core/`, ni los items 1-8 del inventario. La verificación de cierre (lint+audit+build) requiere un rol con shell.
