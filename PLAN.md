# Plan de Trabajo — agent-foundry

Fábrica de agentes y skills agnósticos de modelo/proveedor, con capa de binding
por herramienta (opencode, chatgpt/codex, kiro).

## Principio arquitectónico

`core/` nunca menciona modelos ni rutas de herramientas. Los bindings viven solo
en `profiles/`. Cambiar un modelo o migrar de herramienta = editar 1 YAML + build.

```
core/agents/      Definiciones agnósticas (sin model:, sin rutas absolutas)
core/skills/      Conocimiento técnico puro, una sola vez
core/workflow/    Ciclo de vida, estados y gates = fuente de verdad única
profiles/         models.yaml (tiers) + permissions.yaml (permisos por rol)
adapters/         Generadores: opencode, chatgpt, kiro (motor compartido)
tooling/          build.sh, lint.sh, sync.sh, validate-states.py
evals/            Benchmarks ejecutables de prompts
docs/             Documentación nueva del proyecto
```

## Fases

| #  | Fase | Estado |
|----|------|--------|
| 0  | Scaffold: repo, estructura, PLAN.md | ✅ Hecho |
| 1a | Migrar 28 agentes a core/ sin model:/temperature/permission ni rutas absolutas | ✅ Hecho |
| 1b | Migrar skills deduplicando anidadas; hyprmind a carpetas SKILL.md | ✅ Hecho (62 skills) |
| 2  | workflow/: lifecycle.md, states.md, matrix.yaml (agente × fase × skill) | ✅ v1 inicial (matrix por validar) |
| 3  | profiles/models.yaml con tiers y fallbacks por proveedor | ✅ Datos opencode; chatgpt/kiro vacíos |
| 4  | Adapter opencode con paridad 1:1 respecto a config-ai | ⬜ |
| 5  | Adapters chatgpt (Codex CLI) y kiro | ✅ Hecho (bindings de modelos pendientes de activar en profiles) |
| 6  | Suite ambxst: shell-dev, plugins, theming, packaging + linux-dev | ✅ Hecho (5 skills nuevas en core/skills) |
| 7  | Auditoría de coordinación agente-fase-skill (altas/bajas) | ✅ Hecho (matrix v2; hallazgos 61→10 excepciones documentadas) |
| 8  | Tooling + evals + CI (lint anti-drift, validador de estados) | ✅ lint/build/sync + validate-states.py + evals runner con 4 casos semilla |
| 9  | Cutover final e archivo de config-ai | ✅ Hecho (2026-08-22): sync instalado y verificado byte-a-byte; config-ai congelado |

Comandos nuevos:
```bash
python3 tooling/audit_matrix.py                    # auditoría de coordinación
python3 tooling/validate-states.py <repo-activo>   # valida shared contexts SDD
python3 evals/run.py evals/cases/spec-validator.yaml --executor opencode  # evals reales
```

Notas:
- Fase 6: se eliminó el concepto de staging `docs/skills-src` — las skills
  nuevas viven directamente en `core/skills/` (fuente única).
- Fase 9 (cutover): ejecutar `tooling/sync.sh` para instalar la salida
  generada y congelar config-ai después.

Ver `docs/migration-notes.md` para decisiones detalladas de migración.

## Decisiones tomadas

- **Nombre**: agent-foundry.
- **Adapters primera iteración**: opencode, chatgpt (Codex), kiro. Gemini queda fuera.
- **Migración**: solo agentes y skills; la documentación se escribe desde cero.
- **Skills duplicadas anidadas** (`python-stack/python-stack/`, etc.): la versión
  canónica es la anidada con frontmatter YAML (es la instalada en ~/.config/opencode).
- **config-ai**: se congela como histórico al completar el cutover.
- **Herencia DAE/swarm-forge (R.C. Martin), 2026-08-24**: sin agentes ni skills
  nuevos (anti-solape): política de mutación diferencial + módulos testeables +
  property tests opt-in en `testing-strategy`; CRAP por diff y ejecución
  incremental en `code-quality-and-sonarqube`; gauntlet acotado builder/crítico
  en `design-to-code`; exit criteria por suite existente en `refactor`;
  priorización CRAP-first de lectura en `reviewer`; handoff compacto en
  `states.md §6`; verifier≠implementer + packs (duo/incremental/completo) como
  gate determinista en matrix.yaml + `tooling/check_constraints.py` (lint).
  Decisión de fondo: revisión de código SE MANTIENE (contrario al "no leer
  código" literal de Uncle Bob); lo que se adopta es su profundidad por riesgo
  y el arbitraje por suites ya escritas.
- **Templates de documentos SDD, 2026-08-24**: `templates/` pasa de solo
  MEMORY.md a cubrir todo el ciclo: `sdd-context.md` (pasa validate-states.py
  con 0 errores; firmas de gates como comentarios para no falsificarlas),
  `requirements-brief.md`, `delta-spec.md`, `task-board.md`,
  `design-readme.md`, `technical-debt.md`. `scaffold-project.sh` los instala en
  `docs/templates/` del repo activo. Fuente de formato: las skills dueñas de
  cada documento, no invención nueva.

## Mejoras de coordinación pendientes de discutir (Fase 7)

1. Adoptar `MEMORY.md` (errores → solución → regla para el agente).
2. Estados como enum formal centralizado (hoy viven en prosa por agente).
3. No migrar `functional-test-planner` de gemini (duplica test-architect).
4. Regla anti-drift en lint: fallar si un agente en core/ menciona `model:` o `/home/`.
