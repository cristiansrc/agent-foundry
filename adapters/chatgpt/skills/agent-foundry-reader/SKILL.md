---
name: agent-foundry-reader
description: Analiza repositorios construidos con la filosofía Agent Foundry y explica su arquitectura, agentes, skills, workflow SDD, gates, handoffs y drift en modo estrictamente solo lectura. Exclusiva para ChatGPT Desktop; no usar para OpenCode ni para modificar proyectos.
---

# Agent Foundry Reader

## Propósito

Usa esta skill cuando el usuario pida entender, auditar o explicar un proyecto
que siga la filosofía de Agent Foundry. El objetivo es reconstruir el modelo
mental del proyecto y entregar un análisis verificable, no ejecutar el harness ni
implementar cambios.

## Alcance de lectura

Analiza únicamente el repositorio activo indicado por el usuario. Prioriza, si
existen:

1. `AGENTS.md` y archivos de contexto jerárquicos.
2. Specs activas, contratos OpenAPI, migraciones y configuración runtime.
3. `docs/specs/.working/`, task boards y reportes de validación.
4. Definiciones de agentes, skills, workflow, perfiles y adapters de Foundry.
5. Código, tests, README, runbooks y notas históricas como evidencia secundaria.
6. `graphify-out/GRAPH_REPORT.md` si Graphify está configurado.

No fuerces documentación enterprise ni Master Specs globales: solo aplican si
la estructura del repositorio y sus artefactos lo demuestran.

## Método de análisis

- Determina primero el repositorio y su alcance; no busques en otros proyectos.
- Distingue hechos observados, inferencias, planes, historia y aspectos no
  verificados.
- Reconstruye agentes por rol, fase, responsabilidad, permisos, artefactos que
  consumen/producen y límites de ownership.
- Revisa el flujo SDD, estados canónicos, veredictos, gates humanos,
  descomposición, ejecución, calidad y Git-Ops.
- Contrasta documentación, configuración, código y tests; reporta divergencias
  en vez de resolverlas mentalmente.
- Identifica skills relevantes por dominio y cómo se relacionan con cada agente.
- Revisa tiers de modelo, bindings, fallbacks y políticas de privacidad solo
  como configuración documentada, sin asumir que el modelo está disponible.
- Usa rutas exactas y líneas cuando sea útil para sostener cada hallazgo.

## Salida recomendada

Entrega un mapa con:

1. repositorio y alcance analizado;
2. estructura y fuentes de verdad;
3. agentes, roles y boundaries;
4. skills y dominios técnicos;
5. workflow SDD, estados y gates;
6. handoffs y ownership;
7. modelos, permisos y adapters;
8. Graphify, contratos y artefactos canónicos;
9. drift, contradicciones, riesgos y evidencia faltante;
10. conclusiones e inferencias separadas;
11. recomendaciones para analizar otros proyectos con esta filosofía.

## Restricción estricta de solo lectura

Esta skill nunca debe:

- crear, editar, borrar, mover ni formatear archivos;
- ejecutar builds, installs, syncs, migraciones, despliegues o scripts mutantes;
- ejecutar comandos Git que cambien el estado del repositorio;
- modificar estados SDD, firmas humanas, specs, contratos, código o tests;
- corregir contradicciones silenciosamente;
- afirmar que realizó cambios o validaciones que no estén respaldados por
  evidencia leída en el ciclo actual.

Si falta el repositorio activo, una ruta canónica o evidencia necesaria, declara
el bloqueo y solicita el dato faltante. Las recomendaciones deben permanecer en
el chat.

Esta skill es exclusiva de ChatGPT Desktop/Codex. No forma parte del conjunto de
skills de OpenCode ni debe instalarse en `~/.config/opencode/skills`.
