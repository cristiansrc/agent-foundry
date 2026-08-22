---
name: amazon-sqs-standard
description: Mejores prácticas para Amazon SQS (Visibility Timeout, DLQ, Batching, FIFO).
---

# Estándar Amazon SQS

Guía para el uso eficiente de Amazon SQS como servicio de mensajería gestionado en AWS.

## Configuración de Colas
1.  **Standard vs FIFO**: Usar colas FIFO solo cuando el orden exacto y la deduplicación estricta sean críticos. Para la mayoría de los casos, preferir Standard por su throughput ilimitado.
2.  **Visibility Timeout**: Configurar el timeout para que sea al menos 6 veces el tiempo que tarda el consumidor en procesar el mensaje, para evitar que otros consumidores lo vean antes de terminar.
3.  **Dead Letter Queues (DLQ)**: Configurar siempre una DLQ con un `maxReceiveCount` (típicamente entre 3 y 5) antes de mover el mensaje a la cola de fallos.

## Optimización de Costos y Rendimiento
- **Long Polling**: Configurar `ReceiveMessageWaitTimeSeconds` a 20 segundos para reducir el número de peticiones vacías y ahorrar costos.
- **Batching**: Usar `SendMessageBatch` y `DeleteMessageBatch` para procesar hasta 10 mensajes por petición, optimizando throughput y latencia.
- **Message Retention**: Configurar el tiempo de retención (default 4 días, max 14 días) según la criticidad del negocio.

## Implementación del Consumidor
- **Idempotencia**: Obligatoria mediante el uso de `MessageDeduplicationId` en colas FIFO o manejando manualmente IDs de mensajes en BD/Redis para colas Standard.
- **Delete After Process**: Asegurar que el mensaje se elimine de la cola inmediatamente después de un procesamiento exitoso.
- **Backoff**: Implementar lógica de reintento con retraso progresivo si el consumidor falla.

## Seguridad y Tracing
- **Encryption**: Habilitar SSE (Server-Side Encryption) usando claves KMS.
- **IAM Roles**: Usar roles de ejecución de Lambda o instancias EC2 con los permisos mínimos necesarios (`sqs:SendMessage`, `sqs:ReceiveMessage`, `sqs:DeleteMessage`).
- **AWS X-Ray**: Integrar para trazabilidad de mensajes entre productores y consumidores.

## Detección del Skill
- Activo si se detectan dependencias como `spring-cloud-aws-starter-sqs`, `aws-sdk-java` (v2), `boto3` (Python) o configuraciones de ARN de SQS.
