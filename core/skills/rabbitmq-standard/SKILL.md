---
name: rabbitmq-standard
description: Mejores prácticas para RabbitMQ en Arquitectura Hexagonal (Direct/Topic Exchanges, DLQ, Outbox, Idempotencia).
---

# Estándar RabbitMQ

Este skill define las convenciones para el uso de RabbitMQ como broker de mensajería, asegurando resiliencia, trazabilidad y consistencia de datos.

## Patrones de Arquitectura
1.  **Transactional Outbox**: Para asegurar la consistencia entre la base de datos y el broker. Los eventos se guardan en una tabla `outbox` en la misma transacción de negocio y un relay los publica a RabbitMQ.
2.  **Idempotent Consumer**: Cada consumidor debe verificar si ya procesó el mensaje (ej. usando un `message_id` en una tabla de auditoría o Redis) antes de ejecutar lógica de negocio.
3.  **Dead Letter Exchange (DLX)**: Configurar siempre un DLX y una DLQ para capturar mensajes que fallan después de agotar los reintentos.

## Configuración de Infraestructura
- **Exchanges**: Preferir `Topic Exchange` para máxima flexibilidad o `Direct` para enrutamiento simple. Evitar el default exchange.
- **Durabilidad**: Las colas y exchanges deben ser `durable=true`.
- **Persistencia**: Los mensajes deben marcarse como persistentes (`delivery_mode=2`).
- **Quorum Queues**: Usar Quorum Queues para alta disponibilidad en entornos productivos.

## Resiliencia y Manejo de Errores
- **Reintentos con Backoff**: Implementar reintentos exponenciales. No reencolar (`requeue=true`) inmediatamente si el fallo es persistente.
- **TTL de Mensajes**: Configurar tiempo de vida para evitar que mensajes obsoletos bloqueen las colas.
- **Consumer Acknowledgements**: Usar `manual ack` para confirmar el procesamiento solo después de que la lógica de negocio y la persistencia local hayan tenido éxito.

## Estándares Técnicos (Spring Boot / Python)
- **Naming Convention**: 
    - Exchanges: `<dominio>.<subdominio>.exchange`
    - Queues: `<dominio>.<subdominio>.<proposito>.queue`
    - Routing Keys: `<dominio>.<entidad>.<accion>` (ej. `orders.order.created`).
- **Serialización**: Usar **JSON** (con Jackson en Java o Pydantic en Python) para interoperabilidad. Evitar serialización nativa de Java.
- **Tracing**: Incluir `trace_id` en los headers de RabbitMQ para trazabilidad distribuida.

## Detección del Skill
- Si se detectan dependencias como `spring-boot-starter-amqp` (Java) o `pika`/`aio-pika` (Python) y hay archivos de configuración de RabbitMQ, este skill se considera **ACTIVO**.
