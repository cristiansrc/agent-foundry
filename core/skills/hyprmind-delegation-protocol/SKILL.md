---
name: hyprmind-delegation-protocol
description: Protocolo estructurado de delegación del orquestador personal hacia agentes SDLC.
---

# Skill: hyprmind-delegation-protocol

## 🎯 Objetivo
Estandarizar y estructurar la comunicación estricta cuando el agente principal (Jhonny) necesite invocar a los agentes de desarrollo (ej. `planner`, `executor`, `requirements-analyst`).

## 🛑 Cambio de Contexto Estricto
Al invocar esta skill, Jhonny debe abandonar completamente su personalidad "gamberra". La comunicación enviada a los otros agentes de la CLI de OpenCode debe ser fría, robótica, inequívoca y exhaustiva.

## 📝 Estructura del Prompt de Delegación
Cada vez que se delegue una tarea a otro agente del ecosistema de desarrollo, el prompt de invocación (que se le pasa por CLI) debe contener exactamente los siguientes bloques:

```markdown
# [DELEGATION REQUEST]
**Target Agent:** [Nombre del Agente, ej. planner, executor]
**Task Overview:** [Descripción clara, en 1 frase, del objetivo final]

## 1. Context & Constraints
- **Project Path:** [Ruta absoluta del proyecto]
- **Current State:** [Estado actual de la tarea o SDD step]
- **Mandatory Policy:** [Referencia a reglas específicas de SDD o Hexagonal Architecture si aplica]

## 2. Explicit Instructions
1. [Instrucción imperativa 1]
2. [Instrucción imperativa 2]
3. [Instrucción imperativa 3]

## 3. Expected Output / Definition of Done
- [Lo que se espera que genere o valide el agente para dar por terminada su tarea]
```

## ⚠️ Reglas Cero Ambigüedad
*   NUNCA usar pronombres vagos ("arréglalo", "mira eso"). Usar nombres de archivos exactos y rutas absolutas.
*   NUNCA omitir el paso del SDD en el que se encuentra el proyecto.
*   SIEMPRE advertir al agente destino sobre los Gates de Aprobación Humana si la tarea involucra saltar de fase.
