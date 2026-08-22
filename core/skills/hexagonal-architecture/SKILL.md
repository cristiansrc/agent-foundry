---
name: hexagonal-architecture
description: Implementación de Puertos y Adaptadores (Clean Architecture) con dominio puro, boundaries explícitos, estructura de directorios por tecnología y desacoplamiento total de frameworks.
---

# Arquitectura Hexagonal (Puertos y Adaptadores)

Guía mandatoria para implementar una arquitectura limpia que protege la lógica de negocio de cambios tecnológicos. Esta skill define los boundaries y la **estructura exacta de directorios por stack tecnológico**.

---

## 1. Estructura de Capas y Responsabilidades

### A. Núcleo de Dominio (`domain`)
- **Entidades**: Objetos con identidad propia que contienen la lógica de negocio central.
- **Value Objects**: Objetos inmutables por valor (ej: `Email`, `Money`, `TaxId`).
- **Domain Services**: Lógica de negocio que involucra múltiples entidades.
- **Domain Exceptions**: Excepciones de negocio (ej: `InsufficientBalanceException`).
- **Domain Events**: Hechos del negocio ya ocurridos (ej: `OrderPlacedEvent`).
- **⚠️ REGLA DE ORO**: Dependencia CERO hacia frameworks, JPA, ORM, Jackson, HTTP, JSON, Pydantic, TypeORM, Spring Annotations o SQL. El dominio es 100% Java/Kotlin/Python/Go/TS puro.

### B. Capa de Aplicación (`application`)
- **Input Ports (Interfaces)**: Definen los casos de uso que expone el sistema (ej: `CreateOrderUseCase`).
- **Use Cases (Implementación)**: Orquestan entidades de dominio, transacciones lógicas y puertos de salida.
- **Output Ports (Interfaces)**: Definen lo que la aplicación requiere del exterior (ej: `OrderRepositoryPort`, `PaymentGatewayPort`, `NotificationPort`).
- **DTOs / Commands / Queries / Results**: Objetos de transferencia de entrada/salida de los casos de uso, independientes de HTTP o DB.
- **REGLA**: Depende únicamente de `domain`. No conoce controladores HTTP, entidades JPA ni librerías de infraestructura.

### C. Capa de Infraestructura (`infrastructure`)
- **Driving Adapters (Input)**: Adaptadores de entrada que inician acciones (Controladores REST/FastAPI, Listeners de Kafka/RabbitMQ, CLI, Cron Jobs).
- **Driven Adapters (Output)**: Implementaciones concretas de los `Output Ports` (JPA/SQLAlchemy Repositories, Clientes HTTP Feign/httpx, adaptadores de Email/S3).
- **Mappers**: Mapean entre modelos de infraestructura (DTOs HTTP, Entidades ORM) y entidades de Dominio/DTOs de Aplicación.
- **Configuration / Wiring**: Inyección de dependencias, beans de Spring, contenedores DI, registros de módulos.
- **REGLA**: La infraestructura depende de `application` y `domain`. Dominio y aplicación NUNCA dependen de infraestructura.

---

## 2. Estructura de Directorios Estándar por Tecnología

### ☕ Java / Kotlin (Spring Boot / Micronaut)
```
src/main/java/com/empresa/proyecto/
├── domain/
│   ├── model/ (Entidades, Value Objects)
│   ├── service/ (Domain Services)
│   ├── exception/ (Domain Exceptions)
│   └── event/ (Domain Events)
├── application/
│   ├── port/
│   │   ├── in/ (Input Ports / UseCase Interfaces)
│   │   └── out/ (Output Ports / Repositories Interfaces)
│   ├── usecase/ (Implementaciones de UseCases)
│   └── dto/ (Commands, Queries, DTOs de Aplicación)
└── infrastructure/
    ├── adapter/
    │   ├── in/web/ (REST Controllers, DTOs de entrada, GlobalExceptionHandler)
    │   ├── in/event/ (Kafka/RabbitMQ Listeners)
    │   └── out/persistence/ (JPA Entities, Spring Data Repositories, Adaptador de Salida, Flyway)
    └── config/ (Spring @Configuration, Beans Wiring)
```

### 🐍 Python (FastAPI / Flask)
```
src/
├── domain/
│   ├── models.py (Dataclasses / Entidades Puras)
│   ├── value_objects.py
│   ├── exceptions.py
│   └── services.py
├── application/
│   ├── ports/ (Abstracciones / ABC Classes)
│   │   ├── input_ports.py
│   │   └── output_ports.py
│   ├── use_cases/ (Servicios de Aplicación)
│   └── dtos.py (Pydantic / Dataclasses de Aplicación)
└── infrastructure/
    ├── adapters/
    │   ├── input/ (FastAPI Routers, Middleware, Exception Handlers)
    │   └── output/ (SQLAlchemy Models, Repositorios Alembic/Async, Clientes HTTP)
    └── config/ (Settings, Dependency Injection Container)
```

### 🦫 Go (Golang)
```
internal/
├── domain/
│   ├── entity.go (Structs de Dominio)
│   ├── value_object.go
│   └── repository.go (Interfaces de Output Ports)
├── application/
│   ├── usecase.go (Servicios de Aplicación)
│   ├── dto.go (Request/Response DTOs)
│   └── port.go (Interfaces de Input Ports)
└── infrastructure/
    ├── handler/ (HTTP Handlers / Chi / Gin / Fiber)
    ├── repository/ (GORM / sqlx / Postgres Adaptador)
    └── config/ (Viper, DI container)
```

### 🟦 Node.js / TypeScript (NestJS / Express / React)
```
src/
├── domain/
│   ├── entities/ (Clases o Interfaces puras)
│   ├── value-objects/
│   └── exceptions/
├── application/
│   ├── ports/ (Interfaces Input/Output)
│   ├── use-cases/ (Servicios de Aplicación)
│   └── dtos/
└── infrastructure/
    ├── adapters/
    │   ├── input/ (Controllers, Event Handlers)
    │   └── output/ (TypeORM/Prisma Entities, Repositorios, Axios Clients)
    └── config/ (Nest Modules, Inyección DI)
```

---

## 3. Matriz de Mapeo y Flujo de Datos

```
[ HTTP Request ] ➔ (REST Controller) ➔ [Map to Command] ➔ (Input Port / Use Case)
                                                                 │
                                                                 ▼
[ HTTP Response ] ◄ (REST Controller) ◄ [Map to Response] ◄ (Domain Entity / Result)
                                                                 │
                                                                 ▼ (Llama Output Port)
                                                          (Driven Adapter / JPA)
                                                                 │
                                                                 ▼
                                                          [ Base de Datos ]
```

---

## 4. Reglas Estrictas de Bloqueo (Checklist)

- 🚫 **Bloquear**: Si una entidad de `domain` utiliza `@Entity`, `@Table`, `@JsonProperty`, `BaseModel` de Pydantic o `@Column`.
- 🚫 **Bloquear**: Si un `REST Controller` o `FastAPI Router` invoca directamente un `Repository` de persistencia sin pasar por un `UseCase`.
- 🚫 **Bloquear**: Si la capa de `application` importa clases concretas de `infrastructure` (ej. import `com.empresa.infrastructure.JpaOrderRepository`).
- 🚫 **Bloquear**: Si los modelos de respuesta de API (HTTP Response DTOs) ingresan al `domain` o `application`.
