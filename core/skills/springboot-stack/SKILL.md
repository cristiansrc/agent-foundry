---
name: springboot-stack
description: Convenciones de Spring Boot 2026 (Virtual Threads, Records, Pattern Matching) y estándares de pruebas JaCoCo.
---

# Estándares Spring Boot

## Pruebas y Cobertura
- **Herramientas**: JUnit 5, Mockito, AssertJ, Testcontainers.
- **Cobertura**: Configurar plugin de **JaCoCo** en Gradle/Maven.
- **Exclusiones JaCoCo**: Configurar para ignorar:
    - `**/dto/**`
    - `**/entity/**` (solo si no tienen lógica)
    - `**/config/**`
    - `**/exceptions/**`
    - `*MapperImpl*` (MapStruct)
- **Umbral**: Configurar el check de JaCoCo para que falle si el coverage por archivo testable es menor al **85%** (ideal 100%).

## Mejores Prácticas Spring 2026
1.  **Virtual Threads**: Habilitar `spring.threads.virtual.enabled=true` por defecto en proyectos Java.
2.  **Constructor Injection**: Usar siempre inyección por constructor sobre `@Autowired` en campos.
3.  **Observability**: Integración nativa con Micrometer y OpenTelemetry para trazas y métricas.
4.  **Error Handling**: Usar `@RestControllerAdvice` para centralizar el manejo de excepciones, alineado con `springboot-java-rest-error-response-standards` o `springboot-kotlin-rest-error-response-standards` segun el lenguaje activo.

## Comportamiento Obligatorio
1.  **Sincronización**: El agente Executor debe asegurar que `docs/api/openapi.yaml` se copie a `src/main/resources/openapi.yaml` si hay cambios.
2.  **Flyway**: Las migraciones siempre se buscan en `src/main/resources/db/migration`.
3.  **Configuración**: Preferir archivos `.yaml` sobre `.properties`.

## Detección del Stack
- Si el archivo `build.gradle`, `build.gradle.kts` o `pom.xml` está presente y contiene dependencias de Spring Boot, este skill se considera **ACTIVO**.
