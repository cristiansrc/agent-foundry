---
name: fastapi-rest-error-response-standards
description: Estandariza respuestas HTTP de error en FastAPI con exception handlers globales, Pydantic v2, codigos estables, seguridad, OpenAPI y tests.
---

# FastAPI REST Error Response Standards

Esta skill define el contrato de errores para APIs REST FastAPI. La semantica REST general vive en `restful-standard`; la documentacion OpenAPI vive en `openapi-standard`; las convenciones de framework viven en `fastapi-stack`.

## Alcance
- Aplicar a toda respuesta fallida de API REST: `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`, `503` y equivalentes.
- Centralizar errores con exception handlers registrados en la app o router principal.
- No devolver errores ad hoc desde endpoints.
- Cualquier excepcion no controlada debe terminar en un fallback global `500 INTERNAL_ERROR` con estructura segura.
- Mantener compatibilidad con Pydantic v2.

## Contrato ApiErrorResponse
Usar modelos Pydantic v2:

```python
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiErrorDetail(BaseModel):
    field: str | None = None
    code: str
    message: str
    rejected_value: Any | None = None


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: datetime
    status: int
    error: str
    code: str
    message: str
    path: str
    trace_id: str
    details: list[ApiErrorDetail] = Field(default_factory=list)
```

Reglas:
- `details` siempre debe ser lista; usar `default_factory=list`, no `None`.
- `timestamp` debe representar un instante UTC.
- `code` debe ser string estable de negocio o tecnico; no usar el numero HTTP como `code`.
- No exponer stack traces, clases Python, SQL, tokens, secretos ni mensajes internos.
- Usar `extra="forbid"` para evitar campos accidentales en errores publicos.

## Exception Handlers
Registrar handlers globales:

```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ApiErrorDetail(
                field=".".join(str(part) for part in error["loc"]),
                code="FIELD_INVALID",
                message=error["msg"],
                rejected_value=error.get("input"),
            )
            for error in exc.errors()
        ]

        return error_response(
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            message="The request contains invalid fields.",
            details=details,
        )
```

Reglas:
- Manejar `RequestValidationError` como `400 VALIDATION_ERROR` si el estandar del proyecto separa validacion de entrada de `422`.
- Manejar errores de dominio/aplicacion con excepciones propias y codigos estables.
- Manejar `HTTPException` y normalizarla a `ApiErrorResponse`; no dejar el payload default de FastAPI.
- Manejar fallback `Exception` como `500 INTERNAL_ERROR`.
- Registrar handlers una sola vez durante bootstrap.
- No bloquear el event loop en handlers async.

## Fallback Obligatorio
```python
@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception. trace_id=%s", trace_id(request))
    return error_response(
        request=request,
        status_code=500,
        code="INTERNAL_ERROR",
        message="An unexpected error occurred.",
        details=[],
    )
```

Reglas:
- Debe registrar stack trace solo en logs internos.
- No debe usar `str(exc)` como mensaje publico.
- Debe impedir HTML, strings sueltos, dicts ad hoc o payload default `{"detail": ...}`.

## Funcion de Respuesta
- Centralizar construccion con una funcion tipo `error_response(...)`.
- La funcion debe obtener `path` desde `request.url.path`.
- La funcion debe obtener `trace_id` desde middleware/contexto; si falta, generar uno y propagarlo.
- El `status_code` HTTP debe coincidir con el campo `status`.
- Serializar con `model_dump(mode="json")`.

## Seguridad FastAPI
- Errores de autenticacion deben responder `401` con `AUTHENTICATION_REQUIRED`, `TOKEN_INVALID` o `TOKEN_EXPIRED`.
- Errores de autorizacion deben responder `403 FORBIDDEN`.
- Si la politica exige ocultar existencia de recurso, usar `404`.
- No exponer tokens, claims sensibles ni detalles internos del proveedor de identidad.
- Dependencias de seguridad (`Depends`) deben lanzar excepciones propias o normalizadas por handlers.

## Dominio y Aplicacion
- Servicios no deben retornar `JSONResponse`.
- Dominio/aplicacion deben lanzar excepciones propias con `code` estable o retornar resultados internos que el endpoint traduzca.
- Endpoints no deben inventar estructuras de error.
- Infraestructura HTTP traduce errores a `ApiErrorResponse`.

## OpenAPI
- Documentar `ApiErrorResponse` y `ApiErrorDetail` en OpenAPI.
- Cada endpoint debe declarar errores esperados, no solo `500`.
- Sobrescribir responses default si FastAPI genera `HTTPValidationError` y el proyecto usa `ApiErrorResponse`.
- Runtime, OpenAPI, tests y spec prose deben usar la misma forma.
- Si se conserva `422` para validacion de FastAPI, documentarlo explicitamente y no mezclarlo con `400` sin criterio.

## Tests Obligatorios
- Body invalido retorna `400 VALIDATION_ERROR` o `422` segun decision documentada, con `ApiErrorResponse`.
- Recurso inexistente retorna `404` estandar.
- Conflicto de negocio retorna `409` estandar.
- Excepcion inesperada retorna `500 INTERNAL_ERROR` sin stack trace ni mensaje interno.
- `401` y `403` de dependencias de seguridad usan la misma estructura.
- `trace_id`, `path`, `status`, `error`, `code`, `message`, `timestamp` y `details` siempre existen.
- No existe respuesta default `{"detail": ...}` para errores REST publicos.

## Prohibiciones
- No devolver dicts ad hoc desde endpoints para errores.
- No devolver `{"detail": "..."}` default en contratos publicos.
- No exponer `str(exc)` si puede contener detalles internos.
- No mezclar estructuras de error por router.
- No usar `200` para errores funcionales.
- No documentar en OpenAPI una estructura distinta a runtime.

## Evidencia Esperada
- Funcion o modulo donde se registran exception handlers.
- Modelos Pydantic `ApiErrorResponse` y `ApiErrorDetail`.
- Ejemplos reales para `400` o `422`, `401`, `403`, `404`, `409` y `500`.
- OpenAPI revisado para errores.
- Tests ejecutados o `skipped-with-reason`.
