# Skill: Kotlin Stack Convention (IDIOMA: ESPAÑOL)

Este skill define convenciones de lenguaje, boilerplate y mapeo para proyectos basados en Kotlin moderno (Kotlin 2.x+). Si el proyecto usa Spring Boot, combinar con `springboot-stack` solo para reglas de framework.

## Convenciones de Rutas
- **Source Root**: `src/main/kotlin`
- **Tests Root**: `src/test/kotlin`
- **Packages**: Seguir convención de nombres en minúsculas.

## Mejores Prácticas 2026
1.  **Coroutines**: Uso obligatorio de `suspend functions` y `coroutineScope` para asincronía. Evitar bloqueos de hilo.
2.  **KSP2**: Usar Kotlin Symbol Processing (KSP) v2 para cualquier procesamiento de anotaciones o generación de código.
3.  **Kotlin Serialization**: Preferir `kotlinx.serialization` sobre Jackson para máxima compatibilidad con tipos de Kotlin y K2.
4.  **Inmutabilidad**: Usar `val` y `data classes` por defecto.
5.  **Context Parameters**: Usar parámetros de contexto (Kotlin 2.2+) para inyectar dependencias de forma implícita y limpia.
6.  **Sin Lombok**: No usar Lombok en Kotlin. Kotlin ya provee propiedades, `data class`, default parameters, named arguments, `copy` y null-safety.

## Convenciones de Mapeo Kotlin
- Preferir mapping idiomático con constructores, named arguments, `copy`, extension functions y funciones puras pequeñas.
- Usar extension functions como `fun UserEntity.toDomain(): User` o `fun User.toResponse(): UserResponse` cuando el mapping sea local, claro y mantenible.
- Usar MapStruct solo de forma opcional cuando existan clases con muchos atributos, mappings repetitivos entre capas, compatibilidad Java existente, o una convención previa del proyecto.
- Si se usa MapStruct en Kotlin, justificarlo por complejidad o volumen de atributos y mantener los mappers fuera del dominio puro.
- Evitar mappers manuales gigantes; si una conversion crece demasiado, dividirla en funciones auxiliares o evaluar MapStruct.

## Comportamiento Obligatorio
- El código generado debe aprovechar las características de Kotlin (extension functions, null-safety, named arguments, default values, `copy`). No debe parecer "Java escrito en Kotlin".
- No introducir Lombok ni patrones Java de boilerplate (`get/set` manuales, builders verbosos) salvo interoperabilidad estrictamente necesaria.

## Detección del Stack
- Si existen archivos `.kt` o `.kts`, o la estructura `src/main/kotlin`, este skill se considera **ACTIVO**.
