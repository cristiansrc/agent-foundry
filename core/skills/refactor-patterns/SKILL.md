---
name: refactor-patterns
description: Patrones de refactorización segura.
---

# Patrones de Refactorización

Guía de técnicas para mejorar la estructura del código existente sin alterar su comportamiento externo, asegurando la mantenibilidad a largo plazo.

## Técnicas de Refactorización

### Extract Method
- Identificación de fragmentos de código con una responsabilidad única dentro de una función más grande.
- Creación de una nueva función con un nombre descriptivo para encapsular dicha lógica.
- Reducción de la carga cognitiva al leer el flujo principal.

### Simplification of Conditionals
- Sustitución de condicionales complejos por variables booleanas explicativas.
- Uso de Early Returns para eliminar bloques else innecesarios.
- Aplicación de polimorfismo para reemplazar estructuras switch/if-else extensas basadas en tipos.

### Modularización
- Agrupación de lógica relacionada en módulos o clases cohesivas.
- Definición de límites claros (boundaries) entre diferentes partes del sistema.
- Encapsulamiento de detalles de implementación internos.

### Desacoplamiento de Dependencias Externas
- Introducción de Inyección de Dependencias para facilitar el testing.
- Uso de patrones como Wrapper o Adapter para aislar librerías de terceros.
- Definición de interfaces para interactuar con servicios externos, permitiendo cambios de proveedor sin afectar la lógica de negocio.
