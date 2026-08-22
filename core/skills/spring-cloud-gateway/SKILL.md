---
name: spring-cloud-gateway
description: Estándares y mejores prácticas para la implementación de API Gateways con Spring Cloud Gateway.
---

# Estándares Spring Cloud Gateway

Guía para la implementación de un Gateway robusto, seguro y escalable como punto de entrada único a microservicios.

## Configuración y Enrutamiento
- **Predicados**: Usar predicados de ruta (`Path`) claros y versionados (ej: `/api/v1/orders/**`).
- **Filtros de Ruta**:
    - `StripPrefix`: Ajustar el path antes de enviarlo al microservicio si es necesario.
    - `AddRequestHeader`: Inyectar cabeceras de trazabilidad o seguridad.
- **Dynamic Routing**: Preferir la integración con Service Discovery (Eureka/Consul) usando `lb://service-name` en lugar de URLs estáticas.

## Seguridad e Identidad
- **Token Relay**: Usar `TokenRelayGatewayFilterFactory` para propagar automáticamente tokens JWT de Keycloak hacia los microservicios.
- **Validación de Token**: El Gateway debe ser el primer punto de validación del JWT (ver `keycloak-standard`).
- **CORS**: Configurar políticas de CORS globales en el Gateway para simplificar la gestión en los microservicios.

## Resiliencia y Rendimiento
- **Circuit Breaker**: Implementar `Spring Cloud Circuit Breaker` con Resilience4j para evitar fallos en cascada. Configurar fallbacks para rutas críticas.
- **Rate Limiting**: Usar `RequestRateLimiter` con Redis para prevenir abusos y ataques DoS.
- **Timeout**: Definir tiempos de espera (`connect-timeout`, `read-timeout`) por ruta o globales para evitar bloqueos por servicios lentos.

## Observabilidad y Trazabilidad
- **Correlation ID**: Implementar un filtro global que asegure la presencia de un `X-Trace-Id` (o `trace_id`) en cada peticion y respuesta, alineado con la skill de error response del stack activo.
- **Logs de Acceso**: Configurar logs detallados que incluyan ruta de origen, servicio de destino, status code y tiempo de respuesta.
- **Metrics**: Exponer métricas a través de Actuator para monitoreo con Prometheus/Grafana.

## Documentación Consolidada
- **OpenAPI Aggregation**: El Gateway debe actuar como agregador de la documentación OpenAPI de todos los microservicios subyacentes, exponiendo un único Swagger UI.

## Mejores Prácticas
- Usar **Spring WebFlux** (Netty) para el Gateway debido a su naturaleza no bloqueante y alta concurrencia.
- Mantener la lógica de negocio **fuera** del Gateway; su responsabilidad es solo enrutamiento, seguridad y cross-cutting concerns.
- Versionar las rutas desde el inicio para facilitar migraciones futuras.
