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
2. **Instalación por proyecto**: los agentes y skills viven en el proyecto destino
   (`.opencode/agents/`, `.opencode/skills/`), NO en `~/.config/opencode` global.
   El agente `installer` (en `core/agents/installer/`) lee el manifiesto del flujo
   (`install-manifest.yaml`) y crea la estructura necesaria en el proyecto.
3. **Anti-drift**: `core/` jamás menciona modelos concretos (`model:`, IDs de
   proveedor) ni rutas absolutas `/home/`. El lint lo bloquea.
4. **Fuente única**: temperatura y permisos viven SOLO en
   `profiles/permissions.yaml`; tier→modelo SOLO en `profiles/models.yaml`.
   El `ROUTING` del plugin `model-router` deriva de ahí en el build; jamás se
   hardcodea un modelo en `plugins/` ni en `core/`.
5. **Cambios de agentes o skills**: editar `core/` → lint/tests/evals aplicables →
   `build.sh` → sync completo o `sync.sh --workflow-only` acotado sólo con verificación satisfactoria. Commit únicamente
   cuando el usuario lo solicite. Si eval/instalación bloqueada, declarar fuentes
   y salidas preparadas sin presentar configuración activa como actualizada.
6. **Cambios de perfil** siguen `docs/runbooks/model-change.md` (incluye evals).
7. **Pre-commit activo**: lint + auditoría de matriz corren antes de cada
   commit; no saltarse con --no-hooks salvo emergencia documentada.

## Estructura

| Ruta | Contenido |
|------|-----------|
| `core/agents/{sdlc,personal,installer}/` | Prompts agnósticos por rol + agente instalador |
| `core/skills/<nombre>/SKILL.md` | Conocimiento técnico reutilizable |
| `core/workflow/` | lifecycle, states (enum canónico), matrix, graphify-governance |
| `profiles/*.yaml` | Bindings de ejecución (lo único tool-específico) |
| `plugins/opencode/model-router/` | Template del plugin de routing (placeholder `__ROUTING_JSON__`, sin IDs) |
| `adapters/*/render.py` | Generadores nativos por herramienta (opencode también renderiza `out/plugin/`) |
| `evals/cases/*.yaml` | Suites de regresión de comportamiento (ver `docs/runbooks/evals.md`) |
| `docs/runbooks/` | Procedimientos operativos (model-change, evals, harness, MCPs, Jev) |
| `docs/investigations/` | Investigaciones previas a implementar (no son runbooks) |

## Arquitectura de instalación

Los agentes y skills **viven dentro de cada proyecto**, no en `~/.config/opencode` global.
Esto permite que cada proyecto tenga su propio conjunto de agentes y skills sin
interferir con otros proyectos.

### Estructura en el proyecto destino

```
<proyecto>/
├── .opencode/
│   ├── agents/           # Agentes del flujo (ej. master-orchestrator.md)
│   ├── skills/           # Skills del flujo (ej. spec-driven-development/SKILL.md)
│   └── opencode.json     # Configuración específica del proyecto
├── core/                 # (opcional) Fuente de verdad si el proyecto es un flujo
├── profiles/             # (opcional) Bindings de modelo y permisos
└── ...
```

### Agente Instalador

El agente `installer` (en `core/agents/installer/`) instala flujos completos
en proyectos destino:

1. Recibe la ruta de un flujo (ej. `/mnt/data/Shares/Projects/specForce-alfa`)
2. Lee el manifiesto de instalación (`install-manifest.yaml`)
3. Copia agentes a `.opencode/agents/` del proyecto destino
4. Copia skills a `.opencode/skills/` del proyecto destino
5. Crea la estructura de carpetas adicional si el manifiesto lo indica
6. Actualiza el `opencode.json` del proyecto destino si es necesario

### Manifiesto de instalación

Cada flujo debe tener un `install-manifest.yaml` en su raíz que define:
- Qué agentes instalar (nombre, fuente, modelo, modo)
- Qué skills instalar (nombre, fuente, descripción)
- Qué estructura de carpetas crear
- Qué configuración adicional necesita el proyecto destino

## Verificación antes de cerrar una tarea aquí

```bash
./tooling/lint.sh && python3 tooling/audit_matrix.py && ./tooling/build.sh
```
