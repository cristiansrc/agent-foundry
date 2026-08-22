# Notas de Migración desde config-ai (2026-08-22)

Origen: `/home/cristiansrc/Documentos/Proyectos/config-ai` (se congela como histórico).

## Agentes (28/28 migrados)

- Ubicación nueva: `core/agents/{sdlc/{workers,consultants,validators,guardrails},personal}/`.
- Frontmatter limpiado: se eliminaron `model:`, `temperature:` y `permission:`.
  Ahora viven en `profiles/models.yaml` y `profiles/permissions.yaml`.
- Campo nuevo `role:` en cada agente (worker|consultant|validator|guardrail|personal).
- Referencias a modelos concretos neutralizadas en cuerpo y descriptions.
- Enlaces absolutos rotos (`file:///home/cristiansrc/Documentos/config-ai/...`,
  ruta vieja sin `/Proyectos/`) convertidos a texto plano o `<repo>`.
- Reescrituras semánticas manuales: `general.md` (guardrail agnóstico de tool),
  Validation Guard de `spec-remediator.md` (antes validaba modelo concreto,
  ahora valida identidad del agente validador).

## Skills

- 62 skills en `core/skills/`. Origen: 56 de config-ai + reorganizaciones.
- **Duplicados anidados resueltos**: para `fastapi-stack`, `python-stack` y
  `springboot-stack` la versión canónica es la ANIDADA con frontmatter YAML
  (era la instalada en `~/.config/opencode`). Las versiones externas legacy
  (sin frontmatter, contenido distinto) NO se migraron; quedan en el histórico.
- **hyprmind-delegation-protocol / hyprmind-memory-manager /
  hyprmind-workspace-manager**: eran `.md` sueltos; ahora son carpetas con
  `SKILL.md` y frontmatter nuevo.
- Rutas absolutas limpiadas en `git-ops` y `spec-remediation`.

## No migrados (decisiones)

| Ítem | Motivo |
|------|--------|
| `model-tier-routing` (skill) | Inherente al proveedor. Su tabla de tiers/tipos es la semilla de `profiles/models.yaml`; su política de escalamiento se re-autorará agnóstica en Fase 3+ |
| `skills-review-backlog.md` | Artefacto de proceso de config-ai, ya completado |
| `functional-test-planner` (gemini) | Duplica `test-architect` |
| Todo `active/gemini/` | Gemini fuera de los adapters de primera iteración |
| Docs de config-ai (`ciclo_vida_desarrollo_ia.md`, etc.) | Documentación escrita desde cero en `core/workflow/` |

## Pendientes declarados

1. Adapters chatgpt + kiro: poblar bindings vacíos en profiles (Fase 5).
2. Suite ambxst + linux-dev skills en docs/skills-src/ambxst (Fase 6).
3. Validar matrix.yaml contra los prompts reales (Fase 7).
4. sync.sh de instalación y validador de estados (Fases 8-9).

## Paridad del adapter opencode (verificada 2026-08-22)

Build `adapters/opencode/out` vs instalación viva `~/.config/opencode/agents`:

- **19/28 agentes idénticos byte-a-byte** (frontmatter + cuerpo).
- **9/28 difieren solo por mejoras intencionales**: enlaces file:// rotos
  eliminados, referencias a modelos neutralizadas en cuerpos, guardrail
  `general` reescrito agnóstico, Validation Guard de spec-remediator basado
  en identidad de agente y no en modelo.
- Skills: 62 copiadas; las 3 canónicas ahora tienen SKILL.md en la raíz de su
  carpeta (antes anidadas, p.ej. `python-stack/python-stack/SKILL.md`).
