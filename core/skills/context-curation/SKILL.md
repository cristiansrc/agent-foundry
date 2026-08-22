---
name: context-curation
description: Estrategia de selección de contexto relevante para cada agente.
---

# Context Curation Strategy

Define los criterios para filtrar y proporcionar solo la información estrictamente necesaria a cada agente, optimizando el uso de la ventana de contexto y reduciendo el ruido.

## Estrategias de Filtrado por Dominio

### Seguridad y Autenticación
- Archivos de configuración de seguridad (CORS, JWT, Roles).
- Lógica de Middlewares de autenticación.
- Esquemas de usuarios y permisos.

### Persistencia y Base de Datos
- Definición de Entidades/Modelos.
- Archivos de migración y esquemas.
- Repositorios o DAOs específicos.

### Lógica de Negocio
- Servicios del dominio y entidades relacionadas.
- Especificaciones funcionales y reglas de negocio aplicables.
- Tests unitarios que describen el comportamiento esperado.

### Interfaz y Presentación
- Componentes visuales y hooks/servicios de estado asociados.
- Contratos de la API consumida.
- Estilos y assets relevantes para el componente en cuestión.
