# Skill: Java Stack Convention (IDIOMA: ESPAÑOL)

Este skill define convenciones de lenguaje, boilerplate y mapeo para proyectos basados en Java moderno (Java 21/25+). Si el proyecto usa Spring Boot, combinar con `springboot-stack` solo para reglas de framework.

## Convenciones de Rutas
- **Source Root**: `src/main/java`
- **Tests Root**: `src/test/java`
- **Packages**: Seguir convención de nombres en minúsculas (`com.empresa.proyecto`).

## Mejores Prácticas 2026
1.  **Records**: Usar `record` para DTOs, value carriers e inmutabilidad de datos cuando el framework/libreria lo soporte sin fricción.
2.  **Virtual Threads**: Priorizar el uso de Virtual Threads para tareas de I/O bloqueante (Project Loom). Evitar frameworks reactivos innecesarios.
3.  **Pattern Matching**: Usar `switch` expressions y pattern matching para desestructurar records y manejar jerarquías selladas (`sealed interfaces/classes`).
4.  **Scoped Values**: Usar `ScopedValue` en lugar de `ThreadLocal` para pasar contexto entre hilos de forma segura.
5.  **Lombok**: Usar Lombok de forma estándar para reducir boilerplate en clases Java mutables o gestionadas por frameworks (`@Getter`, `@Setter` solo cuando aplique, `@Builder`, `@RequiredArgsConstructor`, `@NoArgsConstructor` para JPA). Evitar escribir getters/setters/manual builders repetitivos.
6.  **MapStruct**: Usar MapStruct como estándar casi obligatorio para mappings entre capas (API DTO, comandos, dominio, entidades JPA, responses). Evitar mappers manuales repetitivos salvo conversiones triviales de una o dos propiedades o lógica de dominio que no debe delegarse a un mapper generado.

## Convenciones de Mapeo Java
- Los mappers entre capas deben vivir en el adapter o paquete de aplicación correspondiente, no dentro del dominio puro.
- Preferir interfaces `@Mapper(componentModel = "spring")` cuando Spring Boot esté activo.
- Los mappings deben ser explícitos cuando los nombres difieren; no confiar en coincidencias accidentales para campos críticos.
- Usar `@Mapping`, `@BeanMapping`, `@AfterMapping` o métodos auxiliares para normalización técnica; no mezclar reglas de negocio complejas en MapStruct.
- Si el objeto origen/destino tiene muchos atributos, MapStruct es obligatorio salvo justificación explícita en la spec o el patrón existente del proyecto.

## Comportamiento Obligatorio
- El código generado debe ser idiomático de Java moderno, evitando verbosidad innecesaria (ej. usar `var` cuando el tipo sea evidente).
- No escribir conversiones manuales grandes si MapStruct puede generarlas de forma segura.
- No mezclar convenciones Kotlin en Java; `data class`, `copy`, extension functions y null-safety pertenecen a `kotlin-stack`.

## Detección del Stack
- Si existen archivos `.java` o la estructura `src/main/java`, este skill se considera **ACTIVO**.
