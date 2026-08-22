---
name: springboot-kotlin-rest-error-response-standards
description: Estandariza respuestas HTTP de error en APIs Spring Boot Kotlin con RestControllerAdvice, data classes, codigos estables, seguridad, OpenAPI y tests.
---

# Spring Boot Kotlin REST Error Response Standards

Esta skill define el contrato de errores para APIs REST Spring Boot Kotlin. Usa la misma forma publica de `ApiErrorResponse` que `springboot-java-rest-error-response-standards`, pero la implementacion debe ser idiomatica Kotlin. La semantica REST general vive en `restful-standard`; la documentacion OpenAPI vive en `openapi-standard`.

## Alcance
- Aplicar a toda respuesta fallida de API REST: `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`, `503` y equivalentes.
- Centralizar errores HTTP con un unico `@RestControllerAdvice` por aplicacion o bounded context.
- No usar Lombok, builders Java ni DTOs mutables por defecto.
- Controllers no deben construir errores manualmente ni capturar excepciones para formatear respuestas.
- Cualquier excepcion no controlada debe terminar en un fallback global que responda `500 INTERNAL_ERROR` con estructura segura.
- Si el proyecto usa WebFlux/coroutines, mantener el mismo contrato y evitar bloqueos.

## Contrato ApiErrorResponse
Usar `data class` inmutables con valores seguros:

```kotlin
data class ApiErrorResponse(
    val timestamp: Instant,
    val status: Int,
    val error: String,
    val code: String,
    val message: String,
    val path: String,
    @JsonProperty("trace_id")
    val traceId: String,
    val details: List<ApiErrorDetail> = emptyList(),
)

data class ApiErrorDetail(
    val field: String? = null,
    val code: String,
    val message: String,
    @JsonProperty("rejected_value")
    val rejectedValue: Any? = null,
)
```

Reglas:
- El JSON publico debe usar `trace_id` y `rejected_value`, aunque las propiedades Kotlin usen `traceId` y `rejectedValue`.
- `details` siempre debe ser lista; usar `emptyList()`, no `null`.
- `timestamp` debe representar un instante UTC.
- `code` debe ser string estable de negocio o tecnico; no usar el numero HTTP como `code`.
- No exponer stack traces, clases Kotlin/Java, SQL, tokens, secretos ni mensajes internos.

## RestControllerAdvice Kotlin
Implementar el handler global en infraestructura HTTP:

```kotlin
@RestControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(
        exception: MethodArgumentNotValidException,
        request: HttpServletRequest,
    ): ResponseEntity<ApiErrorResponse> {
        val details = exception.bindingResult.fieldErrors.map { error ->
            ApiErrorDetail(
                field = error.field,
                code = "FIELD_INVALID",
                message = error.defaultMessage ?: "Invalid field.",
                rejectedValue = safeRejectedValue(error.rejectedValue),
            )
        }

        return buildError(
            status = HttpStatus.BAD_REQUEST,
            code = "VALIDATION_ERROR",
            message = "The request contains invalid fields.",
            request = request,
            details = details,
        )
    }
}
```

Reglas:
- Usar `@RestControllerAdvice` o `@ControllerAdvice` + `@ResponseBody`.
- Manejar `MethodArgumentNotValidException`, `ConstraintViolationException` y `HttpMessageNotReadableException`.
- Manejar excepciones de dominio/aplicacion con sealed classes, excepciones tipadas o errores internos mapeables, segun convencion del proyecto.
- Handlers especificos deben tener prioridad sobre handlers genericos.
- Evitar `!!`; resolver nullability de forma explicita.
- Usar funciones pequenas para construir respuestas, por ejemplo `buildError(...)`.

## Fallback Obligatorio
```kotlin
@ExceptionHandler(Exception::class)
fun handleUnexpected(
    exception: Exception,
    request: HttpServletRequest,
): ResponseEntity<ApiErrorResponse> {
    logger.error("Unhandled exception. trace_id={}", traceId(), exception)

    return buildError(
        status = HttpStatus.INTERNAL_SERVER_ERROR,
        code = "INTERNAL_ERROR",
        message = "An unexpected error occurred.",
        request = request,
        details = emptyList(),
    )
}
```

Reglas:
- Debe ser el ultimo handler logico.
- Debe registrar stack trace solo en logs internos.
- No debe usar `exception.message` como `message` publico.
- Debe impedir HTML, Whitelabel Error Page, strings sueltos o mapas ad hoc.

## Seguridad Spring
- Integrar `AuthenticationEntryPoint` para `401` con el mismo `ApiErrorResponse`.
- Integrar `AccessDeniedHandler` para `403` con el mismo `ApiErrorResponse`.
- Si Spring Security responde antes del controller, debe conservar el mismo contrato.
- Tokens expirados, ausentes o invalidos deben usar codigos seguros como `TOKEN_EXPIRED`, `TOKEN_INVALID`, `AUTHENTICATION_REQUIRED`.

## Dominio y Aplicacion
- Dominio y aplicacion no deben retornar `ResponseEntity`.
- Dominio debe evitar dependencias Spring.
- Preferir modelos Kotlin inmutables, sealed hierarchies o excepciones tipadas con `code` estable.
- Infraestructura HTTP traduce errores a `ApiErrorResponse`.
- No construir payloads HTTP dentro de servicios de aplicacion.

## OpenAPI
- Documentar `ApiErrorResponse` y `ApiErrorDetail` en `components.schemas`.
- Los campos JSON requeridos son `timestamp`, `status`, `error`, `code`, `message`, `path`, `trace_id` y `details`.
- Cada endpoint debe declarar errores esperados, no solo `500`.
- El runtime, OpenAPI, tests y spec prose deben usar la misma forma.
- Si se usa `springdoc-openapi`, verificar que los nombres serializados respeten `snake_case`.

## Tests Obligatorios
- DTO invalido retorna `400 VALIDATION_ERROR` con `details`.
- JSON invalido retorna `400 INVALID_REQUEST_BODY`.
- Excepcion de dominio retorna el status y `code` esperados.
- Excepcion inesperada retorna `500 INTERNAL_ERROR` sin stack trace ni mensaje interno.
- `401` y `403` generados por Spring Security usan la misma estructura.
- `trace_id`, `path`, `status`, `error`, `code`, `message`, `timestamp` y `details` siempre existen.

## Prohibiciones
- No usar Lombok.
- No devolver mapas ad hoc, strings sueltos ni HTML.
- No mezclar `camelCase` publico con `snake_case` si la API ya adopto `snake_case`.
- No exponer `exception.message` al cliente si puede contener detalles internos.
- No documentar en OpenAPI una estructura distinta a la que retorna runtime.

## Evidencia Esperada
- Clase del handler global y paquete/capa donde vive.
- Ejemplos reales para `400`, `401`, `403`, `404`, `409` o `422`, y `500`.
- Schemas OpenAPI revisados.
- Tests ejecutados o `skipped-with-reason`.
- Confirmacion de serializacion `snake_case` para `trace_id` y `rejected_value`.
