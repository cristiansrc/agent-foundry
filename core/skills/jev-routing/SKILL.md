---
name: jev-routing
description: Enrutamiento tipado mediante Jev para seleccionar agente, nivel de razonamiento y necesidad de intervención humana sin delegar permisos ni ejecución a Jev.
---

# Routing con Jev

Jev es una capa de decisión, no un agente ejecutor. Recibe un contexto compacto
y devuelve elecciones tipadas que el orquestador o el plugin deben validar
contra la matriz, los permisos y los gates de Agent Foundry.

## Cuándo consultar Jev

Consulta Jev solo para los agentes con routing dinámico declarado en el perfil:

- `planner`
- `solution-architect`
- `enterprise-architect`
- `bug-diagnostician`
- `security-reviewer`
- `final-validation`

`master-orchestrator` conserva siempre su modelo fijo y mantiene el contexto.
Los demás agentes conservan su binding estático.

## Contexto mínimo

Envía únicamente la tarea, la fase, el estado SDD, los candidatos permitidos,
los artefactos relevantes por ruta, los findings abiertos, los gates y las
restricciones. No envíes specs completas, código, logs extensos, secretos ni
la conversación completa.

## Decisiones

La consulta debe devolver:

1. `next_agent`: agente permitido para la fase.
2. `reasoning_level`: `low`, `medium`, `high` o `critical`.
3. `needs_human_clarification`: si falta una decisión humana.

Usa la confianza/probabilidades nativas de Choice y Score. No preguntes a Jev
una segunda vez si está seguro de su propia respuesta.

## Política de confianza

- `confidence >= 0.80`: permitir routing automático si no viola reglas locales.
- `0.60 <= confidence < 0.80`: solicitar confirmación humana.
- `confidence < 0.60`: pedir aclaración; no ejecutar el routing.

Los umbrales son señales de control, no sustituyen permisos, validadores ni
aprobaciones humanas.

## Gate post-aprobación

Después de `Human Plan Approval`, si no cambió la spec y no hay decisión
pendiente, enruta directamente a `task-decomposer`. Reactiva `planner` solo si
la aprobación introduce cambios, conflictos o una decisión técnica,
arquitectónica o funcional.
