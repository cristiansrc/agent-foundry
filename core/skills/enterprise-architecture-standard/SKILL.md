---
name: enterprise-architecture-standard
description: Criterios para macro-arquitectura, system landscape, bounded contexts, integraciones, ownership y workspace multi-repos.
---

# Enterprise Architecture Standard

Esta skill define arquitectura macro de ecosistemas y soluciones multi-sistema. No reemplaza `hexagonal-architecture`, que gobierna boundaries internos de cada servicio/proyecto.

## Alcance
- Usar cuando la solucion involucre multiples aplicaciones, microservicios, frontends, jobs, brokers, n8n workflows, bases de datos, proveedores externos o repositorios.
- Definir system landscape, ownership, bounded contexts, contratos entre sistemas, estrategia de datos, integraciones y decisiones transversales.
- No usar esta skill para disenar clases, paquetes internos o patrones dentro de un servicio; eso pertenece a `hexagonal-architecture` y `design-patterns-standard`.

## Artefactos Canonicos
- `docs/architecture/system-landscape.md`: vision macro, sistemas, usuarios, dependencias externas y ownership.
- `docs/architecture/context-map.md`: bounded contexts, relaciones DDD y upstream/downstream.
- `docs/architecture/integration-map.md`: APIs, eventos, colas, jobs, n8n workflows, contratos y SLA/SLO relevantes.
- `docs/architecture/decision-records/ADR-<number>-<title>.md`: decisiones macro no triviales.
- `docs/architecture/workspace-mapping.md`: mapeo de repositorios si existe solution workspace.

Si el proyecto es standalone y no forma parte de una solucion multi-repo, estos artefactos pueden ser `not applicable` con justificacion.

## Modelo C4
- **Level 1 - System Context**: usuarios, sistemas externos, proveedores, canales y dependencias principales.
- **Level 2 - Containers**: aplicaciones, servicios, frontends, workers, brokers, databases y herramientas externas relevantes.
- **Level 3 - Components**: se delega a specs del proyecto y `hexagonal-architecture`.
- No crear diagramas C4 sin texto de soporte: cada elemento debe tener responsabilidad, owner y razon de existir.
- Mantener diagramas y texto sincronizados; drift entre ambos es blocker.

## Bounded Contexts y Ownership
- Cada servicio o modulo mayor debe tener un bounded context explicito o una razon documentada para compartir contexto.
- No compartir entidades canonicas entre servicios. Cada bounded context posee su modelo y traduce mediante contracts o anti-corruption layer.
- Definir owner funcional y owner tecnico por bounded context.
- Definir lenguaje ubicuo por contexto y terminos que no deben reutilizarse fuera de contexto.
- Si dos contextos comparten datos, definir fuente de verdad, modo de sincronizacion, lag permitido y resolucion de conflictos.
- Evitar "shared database" entre servicios; si existe por legado, documentar restricciones y plan de reduccion de acoplamiento.

## Context Mapping
- Para cada relacion entre contextos, clasificar una relacion DDD: `Customer-Supplier`, `Conformist`, `Anti-Corruption Layer`, `Shared Kernel`, `Published Language`, `Open Host Service`, `Partnership` o equivalente.
- Nombrar upstream/downstream.
- Definir que sistema puede cambiar contrato y cual debe adaptarse.
- Si hay Anti-Corruption Layer, documentar donde vive y que modelos traduce.
- `Shared Kernel` solo se permite con ownership compartido, versionado y pruebas de compatibilidad.

## Integraciones y Contratos
- Toda integracion debe declarar tipo: sync API, async event, queue command, webhook, scheduled job, file exchange, n8n workflow o manual operation.
- Para APIs sync, documentar auth, endpoint owner, OpenAPI canonico, timeout, retry policy, idempotency y error contract.
- Para async/events, documentar producer, consumer, topic/queue, schema, key, ordering, retry, dead-letter, idempotency y retention.
- Para n8n workflows, documentar trigger, payload, credenciales referenciadas, retries, compensation, owner y observability.
- Ningun servicio nuevo debe crearse sin integration contract minimo validado.
- Los contratos macro deben enlazar specs/OpenAPI/event schemas reales cuando existan.

## Datos y Consistencia
- Cada datastore debe tener owner unico.
- Definir sistema fuente de verdad para cada dato critico.
- Definir consistencia por flujo: strong, eventual, compensating transaction o manual reconciliation.
- Definir transaction boundary por servicio; no asumir transacciones distribuidas salvo decision explicita.
- Para cambios cross-service, preferir saga/process manager/outbox/inbox cuando aplique.
- Definir politicas de auditoria, retencion, PII, borrado, backups y restore para datos criticos.
- No replicar datos entre contextos sin proposito, TTL/lag esperado y estrategia de reconciliacion.

## Comunicacion Sync vs Async
- Usar sync cuando el usuario o proceso necesita respuesta inmediata y el acoplamiento es aceptable.
- Usar async cuando se busque desacoplamiento, resiliencia, fan-out, procesamiento diferido o consistencia eventual.
- No usar async para ocultar falta de ownership o contrato.
- No usar sync en cascada para flujos largos si puede tumbar el ecosistema; evaluar orchestration/choreography.
- Definir timeouts, retries, circuit breakers, bulkheads y fallback por dependencia critica.

## Cross-Cutting Concerns
- Identidad y acceso: documentar proveedor, tenants/realms, client ids, scopes/roles y ownership. Ver `keycloak-standard` si aplica.
- Observabilidad: definir trace propagation, correlation id, logs, metrics, dashboards y alerts. Ver `observability-standard`.
- Seguridad: definir trust boundaries, data classification, secrets, network exposure y threat assumptions. Ver `security-standards`.
- Deploy/operacion: definir environments, release strategy, rollback, health checks y dependency readiness.
- API gateway: si existe, documentar routing ownership, versioning, auth delegation, rate limits y OpenAPI aggregation.

## Solution Workspace
- Si existe una solucion multi-repo, usar carpeta `projects/` en la raiz del workspace de solucion.
- No usar `proyectos/` como nombre canonico en reglas de agentes o automatizacion.
- El `.gitignore` de la raiz de solucion debe ignorar `projects/*` para no versionar subrepositorios dentro del repo de arquitectura.
- Cada subproyecto mantiene su propio repositorio, lifecycle, tests y versionado.
- `docs/architecture/workspace-mapping.md` debe declarar cada proyecto: ruta relativa, repositorio remoto si aplica, bounded context, owner y estado.
- Los agentes pueden leer arquitectura macro en la raiz de la solucion y codigo en `projects/<repo-name>`, pero los cambios operativos deben limitarse al repositorio activo salvo instruccion explicita.

## ADRs
- Crear ADR para decisiones macro que afecten multiples servicios, datos, seguridad, integraciones, protocolos, eventos, ownership o costos operativos.
- Cada ADR debe incluir contexto, decision, alternativas consideradas, consecuencias, owner, fecha y estado.
- Estados permitidos: `proposed`, `accepted`, `superseded`, `rejected`.
- Una decision superseded debe enlazar el ADR que la reemplaza.

## Reglas de Bloqueo
- Bloquear si se propone un servicio sin bounded context, owner o integration contract.
- Bloquear si dos servicios escriben la misma fuente de datos sin ownership y consistencia definidos.
- Bloquear si un flujo cross-service no define idempotency, retries, timeout o compensation.
- Bloquear si el workspace usa `proyectos/` como ruta canonica en vez de `projects/`.
- Bloquear si diagramas/texto contradicen specs, OpenAPI, event schemas o repositorios reales.
- Bloquear si una decision macro rompe boundaries de `hexagonal-architecture` dentro de los servicios.

## Evidencia Esperada
- Rutas absolutas de artefactos enterprise revisados o creados.
- Lista de bounded contexts y owners.
- Context map con upstream/downstream.
- Integration map con contracts, protocols y consistency model.
- Data ownership matrix para datos criticos.
- ADRs creados o actualizados para decisiones macro.
- Workspace mapping si aplica, usando `projects/`.
