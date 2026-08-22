# AGENTS.md — agent-foundry (meta)

Convenciones para cualquier agente que trabaje DENTRO de este repositorio.

## Qué es este repo

Fábrica de agentes y skills agnósticos. Flujo de datos:

```
core/ (fuente de verdad) -> profiles/ (bindings modelo+permisos)
                         -> adapters/ (render por herramienta) -> out/
```

## Reglas no negociables

1. **Nunca editar `adapters/*/out/` a mano**: se regenera con `tooling/build.sh`.
2. **Nunca instalar directo**: nada se copia manualmente a `~/.config/opencode`;
   solo `tooling/sync.sh`.
3. **Anti-drift**: `core/` jamás menciona modelos concretos (`model:`, IDs de
   proveedor) ni rutas absolutas `/home/`. El lint lo bloquea.
4. **Fuente única**: temperatura y permisos viven SOLO en
   `profiles/permissions.yaml`; tier→modelo SOLO en `profiles/models.yaml`.
5. **Cambios de agentes o skills** requieren: editar `core/` → `build.sh` →
   `sync.sh` → commit. Los tres pasos, siempre.
6. **Cambios de perfil** siguen `docs/runbooks/model-change.md` (incluye evals).
7. **Pre-commit activo**: lint + auditoría de matriz corren antes de cada
   commit; no saltarse con --no-hooks salvo emergencia documentada.

## Estructura

| Ruta | Contenido |
|------|-----------|
| `core/agents/{sdlc,personal}/` | Prompts agnósticos por rol |
| `core/skills/<nombre>/SKILL.md` | Conocimiento técnico reutilizable |
| `core/workflow/` | lifecycle, states (enum canónico), matrix, graphify-governance |
| `profiles/*.yaml` | Bindings de ejecución (lo único tool-específico) |
| `adapters/*/render.py` | Generadores nativos por herramienta |
| `evals/cases/*.yaml` | Suites de regresión de comportamiento |

## Verificación antes de cerrar una tarea aquí

```bash
./tooling/lint.sh && python3 tooling/audit_matrix.py && ./tooling/build.sh
```
