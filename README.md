# agent-foundry

Fábrica de agentes y skills para entornos de desarrollo asistidos por IA.
Fuente de verdad agnóstica de modelo y proveedor, con capa de binding por
herramienta: **opencode**, **chatgpt** (Codex CLI) y **kiro**.

## Cómo funciona

```
core/  ──►  profiles/  ──►  adapters/  ──►  configs instaladas por herramienta
```

1. **`core/`**: agentes (`sdlc/workers|consultants|validators|guardrails`,
   `personal/`), skills y workflow (ciclo de vida SDLC-IA con gates humanos).
   Ningún archivo aquí nombra modelos, proveedores ni rutas de herramientas.
2. **`profiles/`**: qué modelo usa cada agente por tier/proveedor
   (`models.yaml`) y permisos por rol (`permissions.yaml`). Único lugar a
   tocar cuando cambia un modelo o un plan.
3. **`adapters/`**: generan la configuración nativa de cada herramienta a
   partir de core + profiles. Una sola lógica de render en `shared/`.
4. **`tooling/build.sh`**: reconstruye todas las salidas.

## Roles de agentes

| Rol | Agentes |
|-----|---------|
| Workers (obreros) | executor, architect-executor, database-architect, devops-architect, refactor, documentation, spec-remediator, functional-tester-agent, git-executor |
| Consultants (consultores) | requirements-analyst, planner, enterprise-architect, solution-architect, test-architect, task-decomposer, context-curator, master-orchestrator |
| Validators (validadores) | spec-validator, enterprise-spec-validator, api-governance-agent, bug-diagnostician, reviewer, security-reviewer, final-validation |
| Guardrails | general |
| Personal (fuera del SDLC) | hyprmind-orchestrator, hyprmind-deep-thinker, hyprmind-vision-analyst |

## Reglas operativas críticas

1. Aislamiento de proyecto: prohibido escribir fuera del repositorio activo.
2. Gates humanos obligatorios: `awaiting-human-plan-approval` y
   `awaiting-human-qa-approval`. Ver `core/workflow/states.md`.
3. Cobertura mínima: 85% en archivos testables.
4. Git exclusivo de `git-executor`: ningún otro agente ejecuta comandos git.
5. Anti-drift: si un agente menciona `model:` o una ruta absoluta `/home/`
   dentro de `core/`, el lint falla.

## Comandos

```bash
tooling/build.sh          # genera salidas para las 3 herramientas
tooling/lint.sh           # valida anti-drift y consistencia
tooling/sync.sh           # instala las salidas generadas (~/.config/opencode, etc.)
```

*Estado del plan: ver [PLAN.md](PLAN.md).*
