---
name: design-patterns-standard
description: Criterios pragmaticos para aplicar patrones de diseno sin sobreingenieria y respetando boundaries de arquitectura hexagonal.
---

# Design Patterns Standard

Esta skill define cuando aplicar patrones de diseno. No obliga patrones por defecto. Los boundaries arquitectonicos viven en `hexagonal-architecture`; modelos, DTOs y mappings viven en `repository-dto-patterns`; convenciones de lenguaje viven en las skills del stack.

## Principio Central
- Usa un patron solo si resuelve una variabilidad real, reduce acoplamiento o hace explicita una regla que ya existe.
- No introduzcas un patron para "verse enterprise" ni para anticipar variantes no confirmadas.
- Si una solucion simple con funcion, clase, interface o modulo claro es suficiente, preferir la solucion simple.
- Todo patron debe tener un motivo verificable: proveedor intercambiable, algoritmo variable, boundary externo, workflow repetible, creacion compleja o cross-cutting concern.
- Los patrones no pueden violar dependencia hacia adentro: dominio no depende de frameworks, ORM, HTTP, JSON, UI ni DI containers.

## Criterios Antes de Usar un Patron
- Hay al menos dos variantes actuales o una variante futura confirmada por spec.
- El cambio esperado afectaria multiples sitios si no se abstrae.
- El patron mejora testabilidad o reemplazo de infraestructura.
- El nombre del patron ayuda a entender el diseno, no lo oculta.
- El costo de abstraccion es menor que el costo de duplicacion o acoplamiento.

Si ninguno aplica, no uses el patron.

## Patrones Creacionales
- **Factory Method**: usar cuando la creacion depende de tipo de negocio, proveedor, configuracion o feature flag. La factory no debe contener reglas de negocio complejas que pertenezcan al dominio/use case.
- **Abstract Factory**: usar solo cuando se creen familias completas de objetos relacionados, por ejemplo clientes y mappers por proveedor externo.
- **Builder**: usar cuando un objeto tenga construccion realmente compleja o muchas combinaciones opcionales. No es mandatorio para DTOs o entities.
- **Singleton**: evitar implementarlo manualmente. En Spring Boot lo gestiona el container; en FastAPI usar lifecycle/dependencies; en frontend usar servicios/context cuando aplique.

Reglas por lenguaje:
- Java puede usar Lombok `@Builder` segun `java-stack`, pero no debe reemplazar constructors/factories claros cuando haya invariantes.
- Kotlin debe preferir named arguments, default parameters y `copy`; no introducir builders Java-style salvo interoperabilidad estricta.
- Python debe preferir funciones factory o constructors claros; Pydantic no es un Builder, es validacion/DTO.

## Patrones Estructurales
- **Adapter**: patron principal para conectar output ports con infraestructura o APIs externas. En hexagonal, adapter pertenece a `infrastructure`.
- **Facade**: usar para simplificar un subsistema tecnico o integracion compleja. No usar facade para esconder un use case mal dividido.
- **Decorator**: usar para agregar logging, caching, metrics, retries o authorization sin modificar la logica central. En dominio, usarlo solo si el concepto es de negocio.
- **Proxy**: usar para acceso remoto, lazy loading tecnico, seguridad o caching. No filtrar proxies de ORM hacia dominio.
- **Composite**: usar para estructuras jerarquicas reales, por ejemplo menus, trees, rule groups o workflows compuestos.

Reglas de boundary:
- Adapters, proxies y decorators tecnicos viven en infraestructura o configuracion.
- El dominio puede usar patrones estructurales solo cuando expresen lenguaje de negocio puro.
- No usar Proxy/Lazy Loading como excusa para devolver entidades ORM fuera de infraestructura.

## Patrones de Comportamiento
- **Strategy**: usar cuando existan algoritmos intercambiables definidos por negocio o configuracion, por ejemplo tax calculation, pricing, routing o provider selection.
- **Command**: usar para representar intenciones o tareas ejecutables cuando se requiera cola, retry, audit, undo o scheduling. No confundir con application commands simples de use cases.
- **Observer / Pub-Sub**: usar para eventos de dominio o integracion desacoplada. Definir delivery, ordering, retries e idempotency si cruza proceso o servicio.
- **Template Method**: usar con cautela; preferir composicion/Strategy cuando los pasos variables crezcan o cuando herencia complique tests.
- **State**: usar cuando una entidad tenga transiciones explicitas y reglas por estado. Si solo hay un enum simple, no crear State classes.
- **Chain of Responsibility**: usar para pipelines de validacion, policies o handlers donde el orden sea claro y testeable.

## Aplicacion por Stack

### Spring Boot Java/Kotlin
- DI del framework puede materializar Strategy, Factory, Adapter y Decorator.
- AOP puede implementar cross-cutting concerns como metrics, tracing o transactions, pero no debe esconder reglas de negocio.
- Java: interfaces y MapStruct pueden apoyar Adapter/Mapper segun `java-stack`.
- Kotlin: preferir sealed classes, functions, extension functions y data classes cuando simplifiquen el patron.

### Python/FastAPI
- Usar `Protocol` o `abc.ABC` para ports/adapters cuando ayude a testabilidad.
- Usar funciones factory o dependency providers para wiring, no singletons manuales.
- `Depends` pertenece al adapter HTTP/wiring; no debe cruzar a dominio.
- Strategy puede ser una clase, funcion o callable; no crear jerarquias si un callable claro basta.
- Pydantic no implementa patrones de dominio; usarlo para DTOs/settings/payloads segun `python-stack`.

### Frontend React/Angular
- React hooks pueden encapsular stateful behavior, pero no deben convertirse en god hooks.
- Angular services/DI pueden modelar Strategy, Adapter o Facade para APIs externas.
- RxJS Observer/streams deben usarse cuando haya flujos asincronos reales, no para estado local trivial.
- Higher-order components/render props/decorators deben evitarse si un componente o hook explicito es mas claro.

## Naming
- Nombra por rol de negocio primero, patron despues solo si aporta claridad: `TaxCalculationStrategy`, `PaymentProviderAdapter`, `OrderCancellationCommand`.
- Evita nombres genericos como `Manager`, `Processor`, `Handler` o `Service` si no expresan responsabilidad.
- No agregues sufijos de patron si el patron es accidental o interno y no mejora comprension.

## Prohibiciones
- No crear abstract factories, builders, managers o handlers sin variabilidad real.
- No usar herencia profunda para compartir comportamiento si composicion basta.
- No usar patrones para saltarse boundaries de `hexagonal-architecture`.
- No poner annotations de framework o dependencias tecnicas en dominio para implementar un patron.
- No esconder reglas de negocio en mappers, decorators, proxies o aspects.
- No crear un "god facade" que concentre reglas de multiples bounded contexts.
- No usar Singleton manual para estado mutable compartido.

## Evidencia Esperada
- Problema concreto que justifica el patron.
- Variantes actuales o futuras confirmadas.
- Boundary/capa donde vive el patron.
- Alternativa simple considerada y razon de descarte.
- Tests esperados para cada variante o flujo.
- Confirmacion de que el patron no introduce dependencia de dominio hacia infraestructura.
