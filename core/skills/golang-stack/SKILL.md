---
name: golang-stack
description: Estándares de calidad, estructura del proyecto y mejores prácticas de diseño para aplicaciones de Backend en Go / Golang.
---

# Go / Golang Stack Skill

Esta skill define las directrices y estándares de desarrollo para construir microservicios y aplicaciones de alto rendimiento y confiables en Go. El objetivo es asegurar consistencia en la arquitectura, concurrencia segura, manejo adecuado de errores y alta cobertura de pruebas.

## 1. Estructura de Proyecto Estándar (Standard Go Layout)

En consonancia con la Arquitectura Hexagonal y las convenciones de la comunidad de Go, los proyectos deben seguir esta estructura de carpetas:

*   `/cmd/<app-name>/main.go`: Puntos de entrada del ejecutable. Lógica mínima; solo arranca la configuración, inicializa dependencias y levanta servidores.
*   `/internal`: Todo el código de negocio del microservicio. Go prohíbe que otros módulos importen desde esta carpeta, garantizando fronteras de encapsulación.
    *   `/internal/domain`: Modelos de dominio y reglas de negocio puras. No debe importar librerías externas de bases de datos o transporte (cero dependencias externas).
    *   `/internal/ports`: Interfaces (contratos) de entrada (Use Cases, Handlers) y salida (Repositories, API clients).
    *   `/internal/adapters`: Implementaciones de infraestructura.
        *   `/internal/adapters/http`: Controladores REST, routers (ej: Fiber, Gin, Chi).
        *   `/internal/adapters/repository`: Persistencia SQL (`pgx`, `sqlc`, `gorm`).
        *   `/internal/adapters/client`: Adaptadores de servicios externos o clientes de mensajería (Kafka, gRPC).
*   `/pkg`: Código auxiliar reutilizable que *sí* puede ser importado por otros repositorios (ej: wrappers de logger, utilidades de criptografía).
*   `/api`: Contratos OpenAPI y esquemas de payload.

## 2. Mejores Prácticas de Codificación en Go

### A. Manejo de Errores (Error Handling)
*   **Prohibido ignorar errores:** Nunca uses `_ = funcion()` si retorna un error. Valida siempre con `if err != nil`.
*   **Prohibido usar Panic en producción:** Excepto durante el inicio de la aplicación para fallos irrecuperables (como puertos de red ocupados o fallos en conexión a la base de datos). Para lógica de negocio, retorna siempre `error`.
*   **Envoltura de errores (Error Wrapping):** Envuelve los errores para proveer contexto sin perder el error raíz: `fmt.Errorf("contexto: %w", err)`.
*   **Uso de Sentinel Errors:** Define errores semánticos en la capa de dominio utilizando `errors.New` y verifícalos con `errors.Is(err, errSentinel)` o `errors.As`.

### B. Concurrencia y Contexto
*   **Contexto (`context.Context`):** Toda función bloqueante o de red (consultas a base de datos, llamadas HTTP, colas) debe aceptar `ctx context.Context` como primer argumento. Úsalo para propagar tiempos límite (timeouts), cancelaciones y trazas.
*   **Goroutines seguras:** Asegúrate de que las Goroutines que inicialices tengan un ciclo de vida controlado. Evita fugas de memoria (goroutine leaks).
*   **Evitar condiciones de carrera:** Si múltiples goroutines acceden a un recurso compartido, protégelo usando `sync.Mutex`, `sync.RWMutex` o preferentemente mediante el paso de mensajes a través de Canales (Channels).
*   **Concurrencia Estructurada:** Utiliza `golang.org/x/sync/errgroup` al ejecutar tareas paralelas que deban ser canceladas o reportar fallos en conjunto.

### C. Gestión de Dependencias
*   Mantén el `go.mod` y `go.sum` actualizados.
*   Evita dependencias innecesarias de frameworks de gran peso. Prioriza la biblioteca estándar (`net/http`) o enrutadores ligeros (`chi`, `gin`, `fiber`).

## 3. Persistencia de Datos
*   **Generación de Consultas Seguras:** Se prefiere el uso de `sqlc` para compilar código Go seguro a partir de queries SQL crudas antes que un ORM pesado.
*   **Soft Delete y Auditoría:** Toda tabla de negocio debe contar con columnas de auditoría: `created_at`, `updated_at`, `deleted_at` (soft delete) y `updated_by`.
*   **Migraciones:** Utiliza `golang-migrate` o Flyway en Docker para aplicar cambios incrementales de esquemas.

## 4. Pruebas y Cobertura (Testing)
*   **Pruebas Unitarias:** Colocar los archivos de test junto al código que prueban con la extensión `_test.go`. Usa `testing` estándar.
*   **Mocks de Interfaces:** Generar mocks de los puertos (interfaces) utilizando herramientas como `mockery` o `go-mock`. Coloca las pruebas en el paquete `_test` para garantizar que pruebas las cajas negras públicas.
*   **Testcontainers:** Para pruebas de integración reales de repositorios, utiliza `testcontainers-go` levantando contenedores efímeros de PostgreSQL o Redis.
*   **Cobertura:** El umbral mínimo aceptable de cobertura de test es **85%** en archivos testables.

## 5. Formato y Linters
*   **Formateo:** Todo el código debe pasar el formateador oficial `gofmt` y `goimports`.
*   **Linter Obligatorio:** Instalar y configurar `golangci-lint` en el proyecto. Linters obligatorios a activar:
    *   `errcheck` (verifica errores no controlados).
    *   `staticcheck` (análisis estático avanzado).
    *   `govet` (validaciones del compilador).
    *   `gocritic` (mejores prácticas y micro-optimizaciones).
