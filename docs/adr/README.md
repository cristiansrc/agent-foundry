# Architecture Decision Records (ADR)

Registro de decisiones de arquitectura ya tomadas. Un ADR no es un runbook ni
una propuesta: documenta el contexto, la decisión, las consecuencias y la
evidencia que la respalda.

## Convención

- Archivo: `NNNN-titulo-corto.md` (cuatro dígitos, minúsculas, guiones).
- Estados: `Accepted`, `Superseded by ADR-NNNN`, `Deprecated`.
- Una decisión por ADR; las propuestas abiertas viven en
  [`../architecture.md`](../architecture.md) §5–§7, no aquí.
- Si una decisión se revierte, se crea un ADR nuevo que supersede al anterior;
  no se reescribe la historia.
- La autoridad sigue siendo `profiles/*.yaml`, `core/workflow/states.md` y el
  código/tests actuales. Un ADR explica el porqué; no sustituye esas fuentes.

## Índice

| ADR | Decisión | Estado |
|---|---|---|
| [0001](0001-master-orchestrator-sigue-orquestando.md) | `master-orchestrator` sigue orquestando; ChatGPT Desktop observa. | Accepted |
| [0002](0002-mcp-local-lectura-sin-escritura.md) | MCP local stdio de solo lectura, alcance por proyecto y secreto vía Secret Service. | Accepted (fase de observación) |
