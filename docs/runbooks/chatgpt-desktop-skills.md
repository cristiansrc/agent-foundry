# Skills para ChatGPT Desktop

## Propósito

El adapter de ChatGPT Desktop/Codex puede recibir skills de orientación
documental que no pertenecen al harness OpenCode. Estas skills se mantienen en
`adapters/chatgpt/skills/` y se agregan únicamente a
`adapters/chatgpt/out/skills/` durante el build del adapter ChatGPT.

La skill `agent-foundry-reader` permite analizar repositorios siguiendo la
filosofía de Agent Foundry en modo estrictamente solo lectura. No ejecuta el
harness, no modifica proyectos y no debe instalarse en OpenCode.

## Skills desktop-only

- `agent-foundry-reader`: interpreta estructura, agentes, skills, workflow SDD,
  gates, handoffs, perfiles y drift de repositorios Agent Foundry.
- `opencode-control`: consulta local de metadatos de sesiones y eventos.
- `agent-foundry-knowledge`: fuentes y límites del flujo SDD.
- `execution-auditor`: correlación de evidencia y límites de observabilidad.
- `permission-guardian`: clasificación de permisos en simulación.

La conexión y el alcance de las cuatro skills nuevas están en
[chatgpt-opencode-phase1.md](chatgpt-opencode-phase1.md).

Las skills generales `project-context-navigation` y
`documentation-reconciliation` siguen viviendo en `core/skills/` porque también
son reutilizables por otros adapters; el instalador de ChatGPT las incluye como
skills de orientación.

## Flujo de instalación

Desde la raíz del repositorio:

```bash
tooling/build.sh
tooling/sync-chatgpt.sh
```

`tooling/build.sh` genera la salida del adapter ChatGPT. El instalador copia las
tres skills de orientación a `~/.codex/skills` o al directorio indicado por
`CODEX_SKILLS_DIR`.

El adapter OpenCode no recibe `agent-foundry-reader`: solo copia las skills de
`core/skills/`, mientras que la nueva skill está fuera de ese árbol.
