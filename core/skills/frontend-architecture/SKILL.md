---
name: frontend-architecture
description: Arquitectura limpia para React y Angular.
---

# Frontend Architecture Standards

Estándares arquitectónicos para asegurar la escalabilidad y mantenibilidad de las aplicaciones cliente utilizando React o Angular.

## React: Clean Patterns

### Separation of Concerns
- **Components:** Enfocados exclusivamente en la presentación y manejo de UI.
- **Hooks:** Encapsulación de lógica de estado, efectos y reutilización de lógica compleja.
- **Services:** Capa aislada para llamadas a APIs externas y lógica de negocio pura.

### Type Safety
- Uso obligatorio de interfaces y tipos de TypeScript para modelos de datos.
- Tipado estricto de Props y estados locales/globales.

### API Clients
- Aislamiento de la configuración de red (Axios/Fetch) en clientes dedicados.
- Centralización del manejo de errores de red y transformaciones de datos.

## Angular: Enterprise Patterns

### Modularización
- Uso de módulos funcionales y compartidos para organizar la aplicación.
- Implementación de Lazy Loading para optimizar la carga inicial.

### Estado y Reactividad
- Uso de Signals para el manejo de estado reactivo local.
- RxJS para la gestión de flujos de datos asíncronos y eventos complejos.

### Lógica de Negocio
- Centralización de la lógica en Servicios inyectables.
- Comunicación con APIs externas gestionada exclusivamente a través de servicios de infraestructura.
