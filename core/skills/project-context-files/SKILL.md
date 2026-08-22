---
name: project-context-files
description: Patrón de archivos de contexto jerárquicos (.md) heredado de Claude Code/AGENTS.md — cómo estructurar memoria por capas en repositorios activos para que los agentes hereden contexto correcto sin inflar prompts.
---

# Skill: Project Context Files (memoria jerárquica del repo)

Los agentes modernos (Claude Code, Codex, Gemini CLI, OpenCode) cargan
automáticamente archivos `.md` de contexto en cascada: global → raíz del repo →
subdirectorio. Este estándar define cómo mantenerlos en TUS proyectos para que
el contexto correcto llegue al agente correcto sin inflar el prompt.

## Las tres capas

| Capa | Ubicación | Qué vive ahí |
|------|-----------|--------------|
| **Global** | `~/.codex/AGENTS.md` o config global del tool | Preferencias personales transversales (idioma, estilo de respuesta). Mínimo. |
| **Raíz del repo** | `AGENTS.md` | Mapa del proyecto, comandos build/test/lint EXACTOS, convenciones globales, reglas prohibidas, punteros a specs |
| **Subdirectorio** | `<modulo>/AGENTS.md` | Convenciones locales: solo lo que contradice o especializa la raíz (ej.: `services/payments/AGENTS.md` con sus comandos de test) |

Regla de oro: **cada capa añade o refina; nunca duplica**. El archivo más
cercano al archivo que se edita gana.

## Qué entra y qué NO entra en un AGENTS.md de proyecto

ENTRA:
- Comandos exactos (`pnpm --filter web test`, no "corre los tests")
- Estructura de carpetas con propósito de cada una
- Constraints ("NO editar src/generated/", "migraciones solo con revisión")
- Definición de "done" verificable
- Punteros: `docs/specs/master_spec.md`, `docs/api/openapi.yaml`, `MEMORY.md`

NO ENTRA:
- Historia del proyecto ni decisiones viejas (eso va en MEMORY.md / ADRs)
- Reglas que ya existen como skills instaladas (no duplicar springboot-stack)
- Listas enormes de dependencias o TODOs

## Integración con el flujo SDD foundry

En cada repo activo, el AGENTS.md raíz debe incluir esta sección fija:

```markdown
## Flujo de trabajo (agent-foundry)
- Ciclo SDD: docs/specs/ — estados y gates según agent-foundry/core/workflow/states.md
- Git exclusivo del agente git-executor
- Antes de push a ramas estables: pre-push hook exige firma Gate 2
- Lecciones aprendidas: MEMORY.md (leer antes de diseñar/implementar)
- Grafo de conocimiento: graphify-out/ (reglas en graphify-governance)
```

## Mantenimiento vivo

1. Cuando un agente comete un error evitable → corrige el AGENTS.md del
   subdirectorio donde ocurrió (la corrección más cercana al punto de fallo).
2. Cuando algo aplica a todo el repo → sube la regla a la raíz.
3. Revisión trimestral: eliminar reglas obsoletas (un AGENTS.md con mentiras es
   peor que sin AGENTS.md).
4. Límite sano: raíz <150 líneas; subdirectorios <40 líneas.

## Verificación rápida

```bash
# ¿Qué archivos de contexto vería un agente parado aquí?
ls AGENTS.md ../AGENTS.md ../../AGENTS.md 2>/dev/null
# ¿Mencionan comandos reales? ¿Hay contradicciones entre capas?
```
