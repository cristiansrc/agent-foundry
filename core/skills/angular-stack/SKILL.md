# Skill: Angular Stack Convention (IDIOMA: ESPAÑOL)

Este skill define las convenciones de rutas y arquitectura para proyectos Angular modernos (2026).

## Estructura de Carpetas
- **Core API**: `src/app/core/api/` (Donde vive el cliente base y el OpenAPI sincronizado).
- **Features**: `src/app/features/` (Módulos funcionales y componentes standalone).
- **Shared**: `src/app/shared/` (Componentes UI, pipes y directivas reutilizables).
- **Domain/Models**: `src/app/core/models/` (Interfaces y tipos de dominio).

## Convenciones de Rutas
- **OpenAPI Runtime**: `src/app/core/api/openapi.yaml`
- **Tests Root**: Los archivos de test deben vivir junto al componente (`colocation`) con extensión `.spec.ts`.

## Comportamiento Obligatorio
1.  **Standalone Components**: Priorizar `standalone: true` en todos los componentes, directivas y pipes.
2.  **Signals**: Usar Angular Signals (`input`, `output`, `computed`) para la gestión de estado y reactividad.
3.  **Sincronización**: El agente Executor debe asegurar que `docs/api/openapi.yaml` se copie a `src/app/core/api/openapi.yaml`.
4.  **Zoneless**: Evitar la dependencia de `zone.js` y usar estrategias de detección de cambios basadas en señales.

## Detección del Stack
- Si el archivo `angular.json` existe o `package.json` contiene `@angular/core`, este skill se considera **ACTIVO**.
