---
name: refactor-hexagonal-bridge
description: Skill especializada para la transición de sistemas monolíticos o con lógica dispersa hacia Arquitectura Hexagonal de forma segura.
---

# Refactor Hexagonal Bridge Skill

Esta skill guía la transformación de código legado hacia el estándar del repositorio.

## 1. Estrategia de Extracción
1. **Identificar Dominio:** Extraer la lógica de negocio pura de los `Services` de Spring Boot hacia clases de dominio (Domain Services/Entities).
2. **Definir Puertos:** Crear interfaces (Ports) para las dependencias externas (BD, APIs, Colas).
3. **Inyectar Puertos:** Modificar los Casos de Uso para que dependan de las interfaces, no de las implementaciones.

## 2. Preservación de Contratos
- No modificar los endpoints de la API durante la refactorización inicial.
- Asegurar que los mapeos (DTO <-> Domain) mantengan la compatibilidad con el frontend y sistemas externos.

## 3. Pruebas de Regresión
- Antes de refactorizar: Asegurar cobertura de tests de integración.
- Después de refactorizar: Los mismos tests deben pasar sin cambios en sus assertions.
