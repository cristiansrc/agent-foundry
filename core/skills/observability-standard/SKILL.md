# Skill: Observability Standard (IDIOMA: ESPAÑOL)

Este skill define los estándares de monitoreo, logs y trazabilidad para asegurar que todos los servicios sean "visibles" en producción.

## Estándares de Logs
- **Formato**: Preferir JSON para facilitar el parsing por herramientas como ELK o Grafana Loki.
- **Campos Obligatorios**: `timestamp`, `level`, `service_name`, `trace_id`, `span_id`, `message`, `path`, `user_id` (si aplica).
- **Niveles**: 
  - `DEBUG`: Información detallada para desarrollo.
  - `INFO`: Hitos importantes del negocio.
  - `WARN`: Problemas recuperables.
  - `ERROR`: Fallos que requieren atención inmediata.

## Trazabilidad y Métricas
- **OpenTelemetry**: Uso obligatorio de OTel para propagación de contexto (`traceparent`).
- **Métricas Críticas**: Todos los servicios deben exponer:
  - Latencia de peticiones (p95, p99).
  - Tasa de errores por minuto.
  - Saturación (uso de CPU/RAM).
  - Health checks (`/health/live` y `/health/ready`).

## Comportamiento del Agente
- El Executor debe incluir interceptores o middlewares de logging en cada punto de entrada (API, Workers).
- Los logs NO deben contener secretos, contraseñas o datos PII (Personally Identifiable Information).
