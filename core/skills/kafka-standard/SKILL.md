---
name: kafka-standard
description: Mejores prácticas para Apache Kafka (Particiones, Idempotencia, Schema Registry, EOS).
---

# Estándar Apache Kafka

Define las directrices para la implementación de sistemas basados en eventos usando Kafka, optimizando para alto rendimiento y consistencia.

## Arquitectura y Diseño de Eventos
1.  **Particiones y Escalabilidad**: Definir el número de particiones basado en el throughput esperado. Usar keys significativas para asegurar el orden de los mensajes relacionados en la misma partición.
2.  **Schema Registry**: Uso obligatorio de Schema Registry (Confluent/Apicurio) con **Avro** o **Protobuf** para asegurar la evolución de contratos y compatibilidad.
3.  **Exactly-Once Semantics (EOS)**: Habilitar el soporte de transacciones de Kafka cuando se requiere consistencia exacta entre lectura de un tópico y escritura en otro.

## Configuración del Producer
- **Acks=all**: Para garantizar que el mensaje se replique en todos los ISR (In-Sync Replicas).
- **Idempotent Producer**: Habilitar `enable.idempotence=true` para evitar duplicados en reintentos de red.
- **Compression**: Usar `snappy` o `zstd` para optimizar el uso de red y almacenamiento sin sacrificar mucha CPU.

## Configuración del Consumer
- **Consumer Groups**: Usar nombres descriptivos para los grupos de consumo.
- **Auto-Offset Reset**: Preferir `earliest` para nuevos consumidores para no perder datos históricos si es necesario.
- **Manual Commit**: En procesos críticos, gestionar el commit de offsets manualmente después de procesar exitosamente el mensaje.

## Resiliencia y Manejo de Errores
- **Dead Letter Topics (DLT)**: Mensajes que fallan tras reintentos deben enviarse a un tópico `<original-topic>-dlt` para inspección manual.
- **Error Handling Deserialization**: Configurar `ErrorHandlingDeserializer` en Spring para evitar "poison pills" que bloqueen el consumo.

## Naming Conventions
- Topics: `<entorno>.<dominio>.<entidad>.<version>.<evento>` (ej. `prod.sales.order.v1.created`).
- Keys: UUID de la entidad de negocio.

## Detección del Skill
- Activo si existen dependencias como `spring-kafka`, `confluent-kafka-python` o configuraciones de brokers de Kafka.
