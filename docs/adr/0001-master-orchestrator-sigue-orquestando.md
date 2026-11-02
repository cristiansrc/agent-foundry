# ADR-0001: `master-orchestrator` sigue orquestando; ChatGPT Desktop observa

- **Estado:** Accepted
- **Fecha de registro:** 2026-11-01
- **Ámbito:** integración ChatGPT Desktop/Codex–OpenCode, fase de observación.
- **Fuentes:** `docs/runbooks/chatgpt-opencode-phase1.md:1-6,29-44`;
  `adapters/chatgpt/skills/agent-foundry-knowledge/SKILL.md:8-10`;
  `adapters/chatgpt/skills/opencode-control/SKILL.md:6-10`;
  `README.md:255`.

## Contexto

Agent Foundry necesita que ChatGPT Desktop pueda consultar metadatos y auditar
evidencias de un flujo OpenCode sin convertirse en un segundo orquestador. El
riesgo es duplicar autoridad: dos agentes decidiendo, dos formas de ejecutar y
dos lugares donde responder permisos. El workflow ya tiene un orquestador
(`master-orchestrator`) y gates humanos; la integración no debe reemplazarlos.

## Decisión

1. `master-orchestrator` conserva la orquestación, el contexto y las
   delegaciones en OpenCode.
2. ChatGPT Desktop es un cliente externo de **observación y auditoría**:
   consulta metadatos, contrasta evidencias y emite recomendaciones.
3. ChatGPT Desktop **no** responde permisos, no ejecuta tareas, no inicia
   sesiones y no firma Gate 1/Gate 2.
4. La supervisión estratégica futura (§5 de `docs/architecture.md`) se sitúa
   **por encima** de `master-orchestrator`, no en su lugar.
5. Cualquier acción con efectos sigue requiriendo el rol autorizado en OpenCode
   y, cuando corresponda, firma humana.

## Consecuencias

- La autoridad de ejecución queda en un solo lugar (OpenCode).
- La integración puede ser read-only y fallar sin bloquear el flujo.
- Las recomendaciones de Desktop son asesoría, no aprobación.
- Un fallo del puente/MCP degrada la observación, no la ejecución.
- Cambiar esta decisión (dar a Desktop capacidad de ejecutar o aprobar) exige
  un ADR nuevo y una decisión de arquitectura/seguridad, no un ajuste de
  configuración.

## Evidencia

- Fase 1 declara el alcance y los límites.
- Las skills desktop-only repiten que no se ejecuta ni se responde permisos.
- El README describe `master-orchestrator` como agente maestro y orquestador.
- El Permission Guardian y los permisos nativos siguen siendo la autoridad para
  herramientas y rutas.

## No cubierto

Este ADR no decide el diseño del control plane futuro, ni la telemetría v2, ni
la delegación controlada. Esos puntos son propuestas en
`docs/architecture.md` §5–§7.
