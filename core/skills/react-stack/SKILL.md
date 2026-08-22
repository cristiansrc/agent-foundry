# Skill: React Stack Convention (IDIOMA: ESPAÑOL)

Este skill define las convenciones de rutas y arquitectura para proyectos React modernos (2026).

## Estructura de Carpetas (Feature-Sliced Design Simplified)
- **Shared API**: `src/shared/api/` (Donde vive el cliente base y el OpenAPI sincronizado).
- **Features**: `src/features/` (Componentes con lógica de negocio e interacciones).
- **Entities**: `src/entities/` (Modelos de datos, tipos de dominio y lógica de negocio pura).
- **UI Kit**: `src/shared/ui/` (Componentes atómicos/presentacionales sin lógica de negocio).
- **Pages**: `src/pages/` (Composición de componentes a nivel de ruta).

## Convenciones de Rutas
- **OpenAPI Runtime**: `src/shared/api/openapi.yaml`
- **Hooks de API**: `src/shared/api/hooks/` (Gestión de datos con TanStack Query).
- **Tests Root**: Los archivos de test deben vivir junto al componente que prueban (`colocation`) con extensión `.test.tsx`.

## Comportamiento Obligatorio
1.  **Sincronización**: El agente Executor debe asegurar que `docs/api/openapi.yaml` se copie a `src/shared/api/openapi.yaml` si hay cambios o si el archivo de destino falta.
2.  **Estado**: 
    - **Server State**: Usar obligatoriamente TanStack Query para caché y sincronización.
    - **Client State**: Usar Zustand para estado global ligero.
3.  **React 19**: Priorizar el uso de Server Actions, `useActionState` y `useOptimistic` para la gestión de formularios y feedback instantáneo.
4.  **TypeScript**: Tipado estricto para todas las props, estados y respuestas de API.

## Detección del Stack
- Si el archivo `package.json` existe y contiene la dependencia `react`, este skill se considera **ACTIVO**.
