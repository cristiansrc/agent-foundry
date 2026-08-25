# Delta Spec — <increment-name>

> Plantilla de `planner` (skill spec-driven-development §4).
> Destino: docs/specs/increments/<increment-name>.md
> Estado inicial del incremento: planning. No declarar estados posteriores
> (validated-not-executed lo escribe spec-validator tras verdict: ready).

## Contexto
<!-- Relación con specs anteriores y Master Spec. Qué comportamiento existente cambia y por qué ya no es válido (si aplica). -->

## Contratos API
<!-- Endpoints exactos vía OpenAPI. Referencia a docs/api/openapi.yaml y los paths/schemas añadidos o modificados. Nada de "ver código". -->

## Modelo de Datos
<!-- Cambios en tablas, índices, entidades; migraciones Flyway previstas (nombre de archivo incluido). -->

## Lógica de Dominio
<!-- Use Cases y Domain Services afectados/creados; reglas de negocio nuevas. -->

## Integraciones
<!-- Sistemas externos, colas, workflows: retries, timeouts, idempotencia cuando aplique. -->

## Seguridad
<!-- AuthN/AuthZ, permisos por rol, tenant/user boundary, datos sensibles, rate limits, auditoría. -->

## Operación
<!-- Logs, métricas, trazas, health checks, configuración, despliegue local. -->

## Estrategia de Test y Cobertura
| Aspecto | Definición |
|---------|------------|
| Herramientas | <!-- JaCoCo / pytest-cov / vitest coverage --> |
| Exclusiones | <!-- DTOs, @Configuration puras, generados --> |
| Umbral | ≥85% por archivo testable; dominio/application ideal 100% |
| Streams | unitarias+integración Y aceptación/E2E del incremento en verde juntos |
| Adaptadores de entorno | shells mínimos excluidos del cómputo |

## Criterios de Aceptación
- [ ] <!-- checklist que consumirá final-validation; trazables al requirements brief. -->

---
Trazabilidad: docs/specs/requirements/<increment-name>-requirements-brief.md
