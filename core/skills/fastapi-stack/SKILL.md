---
name: fastapi-stack
description: Estandares y mejores practicas para FastAPI alineados con Arquitectura Hexagonal, OpenAPI, Pydantic v2 y separation of concerns.
---

# Estandares FastAPI

Guia para la implementacion de APIs de alto rendimiento con FastAPI y Arquitectura Hexagonal.

## Pruebas y Cobertura
- **Herramientas**: `pytest`, `httpx` (para TestClient), `pytest-asyncio`.
- **Cobertura**: Usar `pytest-cov`.
- **Exclusiones**: Configurar en `pyproject.toml` o `.coveragerc` para ignorar:
    - `app/schemas/*` (equivalente a DTOs)
    - `app/core/config.py`
    - `app/models/*` o `app/infrastructure/persistence/models/*` (si solo son modelos SQLAlchemy/Tortoise)
    - `app/exceptions.py`
- **Umbral**: Configurar `--cov-fail-under=85` para asegurar el minimo del **85%** de cobertura por archivo.

## Arquitectura Hexagonal en FastAPI
A diferencia de Spring Boot, en FastAPI la arquitectura es mas ligera pero sigue los mismos principios:

### 1. Dominio (`app/domain`)
- Modelos de dominio con clases simples, `dataclass` o value objects propios cuando haya reglas de negocio.
- No usar Pydantic request/response models como dominio por defecto; Pydantic pertenece principalmente al borde HTTP, settings o payloads de integracion.
- Excepciones de dominio personalizadas.
- Interfaces (Abstract Base Classes - `abc.ABC`) para los puertos.

### 2. Aplicacion (`app/application`)
- Casos de uso como funciones `async def` o clases de servicio.
- Orquestacion de logica y puertos de salida.

### 3. Infraestructura (`app/infrastructure`)
- **Adapters In**: Routers de FastAPI (`APIRouter`).
- **Adapters Out**: Implementaciones de repositorios (SQLAlchemy 2.x por defecto, Tortoise solo por excepcion), clientes HTTP (HTTPX).
- **Mappers**: Funciones pequenas y explicitas entre Pydantic API models, application commands/results, domain models y ORM models.
- No pasar `Request`, `Depends`, `HTTPException`, `AsyncSession`, ORM models ni Pydantic request models hacia dominio.

## Manejo Global de Errores (Controller Advice)
FastAPI usa `exception_handlers`. Se debe definir un handler global para asegurar consistencia con `fastapi-rest-error-response-standards`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": exc.status_code,
            "error": exc.error_name,
            "code": exc.code,
            "message": exc.message,
            "path": request.url.path,
            "trace_id": request.state.trace_id,
            "details": exc.details
        }
    )
```

## Mejores Practicas RESTful y OpenAPI
- **Pydantic**: Usar alias en Pydantic si se requiere `snake_case` interno y `camelCase` externo, pero el estandar del proyecto prefiere **`snake_case`** global segun `restful-standard`.
- **Dependency Injection**: Usar `Depends` de FastAPI para inyectar casos de uso en los routers.
- **Async**: Usar siempre `async def` para endpoints y operaciones de I/O (BD, APIs externas).
- **Security**: Usar los esquemas integrados de FastAPI para OAuth2/OpenID Connect (alineado con `keycloak-standard`).
- **OpenAPI**: FastAPI genera el contrato automaticamente. Asegurar que las respuestas de error esten documentadas usando el parametro `responses` en los decoradores de los endpoints.
- **Mapping**: Convertir request models a application commands/queries antes de llamar use cases y convertir application/domain results a `response_model` en el adapter HTTP.
 - **Persistencia**: Usar SQLAlchemy 2.x + Alembic como default. Si la app es async, preferir `AsyncSession`; si es sync, usar `Session`.

## Auditoria y Soft Delete
- Aplicar los principios de `jpa-stack` adaptados a SQLAlchemy:
    - Mixins para campos `created_at`, `updated_at`, `deleted`.
    - Uso de "Session Events" o "Global Filters" para implementar Soft Delete automatico.
