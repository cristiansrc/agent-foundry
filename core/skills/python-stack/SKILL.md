---
name: python-stack
description: Estándares y mejores prácticas para el desarrollo con Python 2026.
---

# Estándares Python

Guía para el desarrollo de aplicaciones robustas y mantenibles en Python.

## Entorno y Dependencias
- **Gestión**: Usar `uv` (recomendado por velocidad) o `poetry` para gestión de dependencias y entornos virtuales.
- **Versión**: Python 3.12+ (aprovechando Generic Types y mejoras en `asyncio`).
- **Typing**: Uso obligatorio de Type Hints en todas las funciones y clases. Usar `mypy` o `pyright` para validación estática.

## Estilo y Calidad de Código
- **Formato**: Usar `ruff` para linting y formateo (reemplaza a flake8, isort y black).
- **Naming**: 
    - `snake_case` para funciones, variables y módulos.
    - `PascalCase` para clases.
    - `UPPER_SNAKE_CASE` para constantes.
- **Docstrings**: Formato Google o NumPy para documentar parámetros y retornos.

## Arquitectura y Estructura
- **Modularidad**: Organizar el código en paquetes lógicos con archivos `__init__.py` claros.
- **Configuración**: Usar `pydantic-settings` para manejar variables de entorno y secretos.
- **Pruebas**: Usar `pytest` con `pytest-asyncio` para pruebas unitarias e integración.
