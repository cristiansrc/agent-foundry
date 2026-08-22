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
| 5  | Adapters chatgpt (Codex CLI) y kiro | ⬜ |
| 6  | Suite ambxst: shell-dev, plugins, theming, packaging + linux-dev | ⬜ |
| 7  | Auditoría de coordinación agente-fase-skill (altas/bajas) | ⬜ |
| 8  | Tooling + evals + CI (lint anti-drift, validador de estados) | 🔨 lint.sh creado; falta build/sync/evals |
| 9  | Cutover final e archivo de config-ai | ⬜ |

Ver `docs/migration-notes.md` para decisiones detalladas de migración.

## Decisiones tomadas

- **Nombre**: agent-foundry.
- **Adapters primera iteración**: opencode, chatgpt (Codex), kiro. Gemini queda fuera.
- **Migración**: solo agentes y skills; la documentación se escribe desde cero.
- **Skills duplicadas anidadas** (`python-stack/python-stack/`, etc.): la versión
  canónica es la anidada con frontmatter YAML (es la instalada en ~/.config/opencode).
- **config-ai**: se congela como histórico al completar el cutover.

## Mejoras de coordinación pendientes de discutir (Fase 7)

1. Adoptar `MEMORY.md` (errores → solución → regla para el agente).
2. Estados como enum formal centralizado (hoy viven en prosa por agente).
3. No migrar `functional-test-planner` de gemini (duplica test-architect).
4. Regla anti-drift en lint: fallar si un agente en core/ menciona `model:` o `/home/`.
