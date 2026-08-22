---
name: springboot-java-rest-error-response-standards
description: Estandariza respuestas HTTP de error en APIs Spring Boot Java con RestControllerAdvice, ApiErrorResponse, codigos estables, seguridad, OpenAPI y tests.
---

# Spring Boot Java REST Error Response Standards

Esta skill define el contrato de errores para APIs REST Spring Boot Java. La semantica REST general vive en `restful-standard`; la documentacion del contrato vive en `openapi-standard`.

Para Spring Boot Kotlin usar `springboot-kotlin-rest-error-response-standards`. Para FastAPI usar `fastapi-rest-error-response-standards`.

## Alcance
- Aplicar a toda respuesta fallida de API REST: `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`, `503` y equivalentes.
- No envolver respuestas exitosas `200`, `201`, `202` o `204` si el contrato de exito ya esta definido.
- Centralizar errores HTTP con un unico `@RestControllerAdvice` por aplicacion o bounded context.
- Evitar `try/catch` repetido en controllers para formatear errores.
- Controllers solo deben traducir request/response; la conversion de excepciones a HTTP vive en infraestructura.
- Cualquier excepcion no controlada debe terminar en un fallback global que responda `500 INTERNAL_ERROR` con estructura segura.
- No depender del error handler por defecto de Spring Boot para APIs JSON.

## Contrato ApiErrorResponse
Usar una estructura estable, serializable y documentada en OpenAPI:

```json
{
  "timestamp": "2026-05-09T18:30:00Z",
  "status": 400,
  "error": "BAD_REQUEST",
  "code": "VALIDATION_ERROR",
  "message": "The request contains invalid fields.",
  "path": "/api/users",
  "trace_id": "4f0f6d2c6b1d4c8a",
  "details": [
    {
      "field": "email",
      "code": "EMAIL_INVALID",
      "message": "must be a well-formed email address",
      "rejected_value": "bad-email"
    }
  ]
}
```

Campos obligatorios:
- `timestamp`: instante UTC ISO-8601.
- `status`: HTTP status numerico.
- `error`: nombre estandar del status HTTP, por ejemplo `BAD_REQUEST`.
- `code`: codigo estable de negocio o tecnico, apto para frontend/i18n.
- `message`: mensaje seguro para cliente.
- `path`: path solicitado.
- `trace_id`: correlacion de request en `snake_case`.
- `details`: arreglo; puede estar vacio, pero no debe cambiar de tipo.

## ApiErrorDetail
- Usar `details` para errores de campo, constraints, conflictos especificos o informacion accionable segura.
- Para validaciones de campos, incluir `field`, `code`, `message` y `rejected_value` solo si el valor rechazado no expone datos sensibles.
- Usar `snake_case` para atributos del contrato, alineado con `restful-standard`.
- No incluir stack traces, clases Java, SQL, tokens, secretos ni mensajes internos.

## Status Codes y Codigos Estables
- `400 BAD_REQUEST`: request mal formado, tipos invalidos, JSON invalido o Bean Validation de entrada.
- `401 UNAUTHORIZED`: token ausente, invalido o expirado.
- `403 FORBIDDEN`: usuario autenticado sin permisos.
- `404 NOT_FOUND`: recurso inexistente o no visible por politica de seguridad.
- `409 CONFLICT`: duplicados, conflicto de estado o concurrencia optimista.
- `422 UNPROCESSABLE_ENTITY`: regla de negocio invalida con request sintacticamente correcto.
- `429 TOO_MANY_REQUESTS`: rate limit.
- `500 INTERNAL_SERVER_ERROR`: error inesperado.
- `503 SERVICE_UNAVAILABLE`: dependencia temporalmente no disponible.
- `code` no debe contener el numero HTTP; debe ser un string estable como `USER_ALREADY_EXISTS`, `VALIDATION_ERROR` o `INTERNAL_ERROR`.

## RestControllerAdvice
Implementar el handler global en infraestructura HTTP:

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(MethodArgumentNotValidException.class)
  ResponseEntity<ApiErrorResponse> handleValidation(
      MethodArgumentNotValidException exception,
      HttpServletRequest request
  ) {
    var details = exception.getBindingResult().getFieldErrors().stream()
        .map(error -> ApiErrorDetail.field(
            error.getField(),
            "FIELD_INVALID",
            error.getDefaultMessage(),
            safeRejectedValue(error.getRejectedValue())
        ))
        .toList();

    return build(HttpStatus.BAD_REQUEST, "VALIDATION_ERROR",
        "The request contains invalid fields.", request, details);
  }
}
```

Reglas:
- Usar `@RestControllerAdvice` o `@ControllerAdvice` + `@ResponseBody`.
- Manejar `MethodArgumentNotValidException` y `ConstraintViolationException`.
- Manejar `HttpMessageNotReadableException` como `400 INVALID_REQUEST_BODY`.
- Manejar errores de dominio/aplicacion con excepciones propias y codigos estables.
- Manejar `AccessDeniedException` como `403`.
- Manejar excepciones no controladas con `500 INTERNAL_ERROR` y mensaje generico.
- Loguear el error real en backend con `trace_id`, pero responder datos seguros al cliente.
- Handlers especificos deben tener prioridad sobre handlers genericos.
- Usar `@ExceptionHandler(RuntimeException.class)` solo si no oculta excepciones de dominio mas especificas.

## Fallback Obligatorio
Todo servicio debe impedir respuestas inconsistentes, HTML o Whitelabel Error Page.

```java
@ExceptionHandler(Exception.class)
ResponseEntity<ApiErrorResponse> handleUnexpected(
    Exception exception,
    HttpServletRequest request
) {
  log.error("Unhandled exception. trace_id={}", traceId(), exception);

  return build(
      HttpStatus.INTERNAL_SERVER_ERROR,
      "INTERNAL_ERROR",
      "An unexpected error occurred.",
      request,
      List.of()
  );
}
```

Reglas del fallback:
- Debe ser el ultimo handler logico.
- Debe registrar stack trace solo en logs internos.
- No debe usar `exception.getMessage()` como `message` publico.
- Debe incluir todos los campos obligatorios de `ApiErrorResponse`.
- Debe evitar respuestas HTML, mapas ad hoc o estructuras distintas.

## Seguridad Spring
- Integrar `AuthenticationEntryPoint` para `401` con el mismo `ApiErrorResponse`.
- Integrar `AccessDeniedHandler` para `403` con el mismo `ApiErrorResponse`.
- Si Spring Security produce una respuesta antes del controller, esa respuesta debe conservar el mismo contrato.
- No revelar si un usuario, tenant o recurso existe cuando la politica de seguridad exija ocultarlo; usar `404` si corresponde.
- Tokens expirados, ausentes o invalidos deben usar codigos diferenciables y seguros, por ejemplo `TOKEN_EXPIRED`, `TOKEN_INVALID`, `AUTHENTICATION_REQUIRED`.

## Dominio y Aplicacion
- Dominio y aplicacion no deben retornar `ResponseEntity`.
- Dominio debe preferir excepciones puras sin dependencia de Spring cuando sea viable.
- Aplicacion puede lanzar excepciones con `code` estable y estado HTTP mapeable.
- Infraestructura HTTP traduce excepciones a `ApiErrorResponse`.
- No construir payloads HTTP dentro de servicios de aplicacion.
- No mezclar errores de negocio con errores tecnicos genericos.

Ejemplo de excepcion de aplicacion:

```java
public class BusinessException extends RuntimeException {
  private final String code;
  private final HttpStatus status;
}
```

## OpenAPI
- Documentar `ApiErrorResponse` y `ApiErrorDetail` en `components.schemas`.
- `ApiErrorResponse` debe requerir `timestamp`, `status`, `error`, `code`, `message`, `path`, `trace_id` y `details`.
- Reutilizar `components.responses` para `BadRequest`, `Unauthorized`, `Forbidden`, `NotFound`, `Conflict`, `UnprocessableEntity`, `TooManyRequests`, `InternalServerError` y `ServiceUnavailable`.
- Cada endpoint debe declarar errores esperados, no solo `500`.
- El media type de error debe ser consistente. Usar `application/json` para `ApiErrorResponse`, salvo decision explicita de adoptar `application/problem+json`.
- Si el proyecto adopta RFC 9457 `ProblemDetails`, no mezclarlo con `ApiErrorResponse` sin adaptador documentado y decision explicita en shared context.
- Spec prose, OpenAPI, tests y handler runtime deben usar la misma forma. Cualquier diferencia de campos o tipos es blocker.

## Tests Obligatorios
- DTO invalido retorna `400 VALIDATION_ERROR` con `details`.
- JSON invalido retorna `400 INVALID_REQUEST_BODY`.
- Recurso inexistente retorna `404` estandar.
- Conflicto de negocio retorna `409` estandar.
- Regla de negocio invalida retorna `422` cuando el proyecto usa esa separacion.
- Excepcion inesperada retorna `500 INTERNAL_ERROR` sin stack trace ni mensaje interno.
- `trace_id`, `path`, `status`, `error`, `code`, `message`, `timestamp` y `details` siempre existen.
- `401` y `403` generados por Spring Security usan la misma estructura.
- No existe respuesta HTML, Whitelabel Error Page, string suelto ni mapa ad hoc para errores REST.

## WebFlux
- Si el proyecto usa Spring WebFlux, aplicar el equivalente con `@RestControllerAdvice` reactivo o `ErrorWebExceptionHandler`.
- Mantener el mismo contrato `ApiErrorResponse`.
- No mezclar estructuras entre endpoints MVC y WebFlux dentro del mismo servicio.

## Prohibiciones
- No devolver strings sueltos como error.
- No devolver mapas ad hoc por controller.
- No exponer `exception.getMessage()` si puede contener detalles internos.
- No mezclar estructuras de error por endpoint.
- No usar `200` para representar errores funcionales.
- No repetir `try/catch` por controller para mapear excepciones.
- No dejar excepciones no controladas fuera del advice global.
- No depender de Spring Boot Whitelabel Error Page para APIs REST.
- No documentar en OpenAPI una estructura distinta a la que retorna runtime.

## Evidencia Esperada
- Clase del handler global y paquete/capa donde vive.
- Ejemplos de errores reales para `400`, `401`, `403`, `404`, `409` o `422`, y `500`.
- Schemas OpenAPI `ApiErrorResponse` y `ApiErrorDetail` revisados.
- Tests ejecutados o `skipped-with-reason`.
- Confirmacion de que Spring Security conserva el mismo contrato de error.
