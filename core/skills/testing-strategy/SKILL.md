---
name: testing-strategy
description: Estrategia unificada de pruebas, metodología TDD (Red-Green-Refactor), pruebas de concurrencia, tests de arquitectura y cobertura mínima para múltiples stacks.
---

# Estrategia Global de Pruebas, TDD y Cobertura

Guía mandatoria para asegurar calidad de software mediante la metodología **Test-Driven Development (TDD)**, pruebas de concurrencia, verificación de arquitectura y una cobertura mínima estricta por archivo testable.

---

## 1. Metodología TDD (Test-Driven Development / Desarrollo Guiado por Pruebas)

Todo desarrollo de código nuevo o corrección de bugs debe seguir el ciclo **Red-Green-Refactor** antes de escribir código de producción:

```mermaid
graph LR
    RED[1. RED: Escribir Test que Falla] ➔ GREEN[2. GREEN: Escribir Código Mínimo para Pasarlo]
    GREEN ➔ REFACTOR[3. REFACTOR: Limpiar Código Preservando Tests en Verde]
    REFACTOR ➔ RED
```

1. **🔴 Fase RED (Test-First)**:
   - Basándose en los Criterios de Aceptación de la spec validada, escribir las pruebas unitarias de las Entidades de Dominio o Casos de Uso *antes* de escribir la implementación.
   - Ejecutar la prueba y verificar que **falla** por la razón esperada (ausencia de método o regla de negocio no cumplida).
2. **🟢 Fase GREEN (Código Mínimo)**:
   - Escribir la cantidad mínima de código de producción indispensable para hacer pasar la prueba.
   - No agregar optimizaciones ni características prematuras fuera del alcance de la prueba activa.
3. **🔵 Fase REFACTOR (Mantenibilidad)**:
   - Refactorizar el código de producción e infraestructura aplicando principios SOLID y Arquitectura Hexagonal.
   - Ejecutar la suite de pruebas para certificar que todo continúa en verde.

---

## 2. Tipos de Pruebas Obligatorias (Pirámide Completa)

### A. Pruebas Unitarias (Unit Testing)
- **Alcance**: Dominio puro (`domain`), Value Objects, Domain Services y Casos de Uso (`application`).
- **Requisito**: Ejecución ultra-rápida (milisegundos) en memoria, sin mocks de negocio complejos, sin conexión a BD real ni frameworks externos.

### B. Pruebas de Concurrencia y Condiciones de Carrera (Concurrency & Race Condition Testing)
- **Alcance**: Rutas de alto tráfico, procesamiento de pagos, actualización de inventarios o estados concurrentes.
- **Técnica**:
  - Ejecución de peticiones paralelas mediante `ExecutorService`, `CountDownLatch` o corrutinas simulando múltiples usuarios simultáneos.
  - Verificación de bloqueo optimista (`@Version`) o pesimista (`SELECT ... FOR UPDATE`), idempotencia y prevención de *Lost Updates* o condiciones de carrera.

### C. Pruebas de Arquitectura y Reglas de Capas (Architecture & Layer Enforcement Testing)
- **Alcance**: Verificación automatizada de los boundaries de Arquitectura Hexagonal en cada build/PR para garantizar que el dominio permanezca 100% puro.
- **Implementación por Stack**:

  #### ☕ Java / Kotlin (Spring Boot) - **ArchUnit**
  Todo proyecto JVM debe incluir un test de arquitectura obligatorio (`HexagonalArchitectureTest.java`):
  ```java
  @AnalyzeClasses(packages = "com.empresa.proyecto", importOptions = ImportOption.DoNotIncludeTests.class)
  public class HexagonalArchitectureTest {

      @ArchTest
      public static final ArchRule domain_debe_ser_independiente_de_infraestructura =
          noClasses()
              .that().resideInAPackage("..domain..")
              .should().dependOnClassesThat()
              .resideInAPackage("..infrastructure..");

      @ArchTest
      public static final ArchRule domain_debe_ser_independiente_de_frameworks =
          noClasses()
              .that().resideInAPackage("..domain..")
              .should().dependOnClassesThat()
              .resideInAnyPackage("org.springframework..", "jakarta.persistence..", "com.fasterxml.jackson..");

      @ArchTest
      public static final ArchRule controladores_solo_deben_llamar_ports_o_usecases =
          classes()
              .that().resideInAPackage("..infrastructure.adapter.in.web..")
              .should().onlyAccessClassesThat()
              .resideInAnyPackage("..infrastructure.adapter.in.web..", "..application.port.in..", "..application.dto..", "java..");
  }
  ```

  #### 🐍 Python (FastAPI) - **pytest-archon** / **import-linter**
  Todo proyecto Python debe incluir la verificación de aislamiento en `tests/test_architecture.py`:
  ```python
  from pytest_archon import archrule

  def test_domain_isolation():
      (
          archrule("domain_must_not_import_infrastructure")
          .exclude("src.domain..")
          .should_not_import("src.infrastructure..", "fastapi..", "sqlalchemy..")
          .check("src.domain")
      )
  ```

  #### 🟦 Node.js / TypeScript - **dependency-cruiser**
  Todo proyecto TypeScript debe incluir el contrato en `.dependency-cruiser.js`:
  ```javascript
  module.exports = {
    forbidden: [
      {
        name: 'domain-no-infrastructure',
        severity: 'error',
        from: { path: '^src/domain' },
        to: { path: '^src/infrastructure|^src/application|node_modules' }
      }
    ]
  };
  ```

### D. Pruebas de Integración con Testcontainers (Integration Testing)
- **Alcance**: Adaptadores de persistencia, consultas de repositorio, scripts de Flyway, adaptadores de mensajería (Kafka/RabbitMQ) y clientes HTTP externos.
- **Técnica**: Uso de **Testcontainers** para levantar contenedores efímeros de PostgreSQL, MySQL, Redis o LocalStack durante la ejecución del test. Prohibido usar H2 para simular PostgreSQL en producción.

### E. Pruebas de Contrato y API (Contract & API Testing)
- **Alcance**: Controladores REST, OpenAPI schemas, serialización JSON, códigos de estado HTTP y middleware de autenticación (JWT/Keycloak).

### F. Pruebas Funcionales UI / E2E (Functional Testing)
- **Alcance**: Flujos críticos de usuario frontend guiados por `functional-tester-agent` mediante MCP de Puppeteer o Playwright.

---

## 3. Matriz de Cobertura y Exclusiones

- **Cobertura Mínima Obligatoria**: **85%** por archivo testable.
- **Ideal en Dominio**: **100%** de cobertura en clases de `domain` y `application`.

| Categoría | Incluido (Test Obligatorio) | Excluido (No cuenta para Coverage) |
|---|---|---|
| **Dominio & Aplicación** | Domain Services, Use Cases, Value Objects, Domain Logic | Interfaces / Ports sin código |
| **Infraestructura** | Custom Repositories, Mappers, Adaptadores, Event Listeners | Clases `@Configuration` puras, `.env`, `.yaml` |
| **Transporte & UI** | Controllers, Exception Handlers, State Guards | DTOs pasivos de datos sin lógica |
| **Código Generado** | NO testear código generado por OpenAPI Generator o MapStruct |

---

## 4. Herramientas por Stack Tecnológico

| Stack | Framework de Test | Cobertura | ArchUnit / Concurrencia |
|---|---|---|---|
| **Spring Boot (Java/Kotlin)** | JUnit 5 + Mockito + Testcontainers | JaCoCo | **ArchUnit** + `CountDownLatch` |
| **FastAPI (Python)** | pytest + httpx/TestClient + Testcontainers | pytest-cov | `import-linter` + `asyncio.gather` |
| **Node.js (TS) / React** | Vitest / Jest + Playwright / Puppeteer | Istanbul / v8 | Dependency Cruiser |

---

## 5. Reglas de Bloqueo

- 🚫 **Bloquear**: Si se implementa código de producción sin haber escrito primero la prueba (violación de TDD).
- 🚫 **Bloquear**: Si la cobertura por archivo testable queda por debajo del **85%**.
- 🚫 **Bloquear**: Si las pruebas utilizan bases de datos H2 o mocks que simulan comportamiento de persistencia real en lugar de Testcontainers.
- 🚫 **Bloquear**: Si las pruebas de arquitectura de ArchUnit detectan que `domain` depende de `infrastructure`.
