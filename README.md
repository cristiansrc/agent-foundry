# agent-foundry

Fábrica de agentes y skills para entornos de desarrollo asistidos por IA.
Fuente de verdad agnóstica de modelo y proveedor, con capa de binding por
herramienta: **opencode**, **chatgpt** (Codex CLI) y **kiro**.

### Índice

- [Cómo funciona](#cómo-funciona)
- [Roles de agentes](#roles-de-agentes)
- [Reglas operativas críticas](#reglas-operativas-críticas)
- [Comandos](#comandos)
- [MCPs (Model Context Protocol) en OpenCode](#mcps-model-context-protocol-en-opencode)
  - [Configuración de AWS](#configuración-de-aws)
- [Agentes](#agentes)
  - [Ciclo de desarrollo de software (27)](#ciclo-de-desarrollo-de-software-27)
- [Skills](#skills-76)
  - [Arquitectura y Metodología](#arquitectura-y-metodología)
  - [Backend y Lenguajes](#backend-y-lenguajes)
  - [Datos y Mensajería](#datos-y-mensajería)
  - [Frontend y Diseño UI/UX](#frontend-y-diseño-uiux)
  - [Seguridad y Calidad](#seguridad-y-calidad)
  - [Orquestación y Documentación](#orquestación-y-documentación)
  - [Sistema Local (ambxst / Linux)](#sistema-local-ambxst--linux)
  - [Otras](#otras)
- [Modelos por herramienta](#modelos-por-herramienta)
  - [OpenCode](#opencode--bindings-activos)
  - [ChatGPT (Codex CLI)](#chatgpt-codex-cli--bindings-activos)
- [Kiro](#kiro--bindings-activos)
- [Skills para ChatGPT Desktop](#skills-para-chatgpt-desktop)

## Cómo funciona

```
core/  ──►  profiles/  ──►  adapters/  ──►  configs instaladas por herramienta
```

1. **`core/`**: agentes (`sdlc/workers|consultants|validators|guardrails`,
   `personal/`), skills y workflow (ciclo de vida SDLC-IA con gates humanos).
   Aquí NO viven bindings: ningún archivo nombra modelos ni proveedores
   concretos ni rutas de herramientas. Las referencias a modelos son genéricas
   («el modelo asignado en el perfil de ejecución»); los valores reales
   (qué modelo, qué temperatura, qué permisos) están únicamente en `profiles/`.
2. **`profiles/`**: qué modelo usa cada agente por tier/proveedor
   (`models.yaml`) y permisos por rol (`permissions.yaml`). Único lugar a
   tocar cuando cambia un modelo o un plan.
3. **`adapters/`**: generan la configuración nativa de cada herramienta a
   partir de core + profiles. Una sola lógica de render en `shared/`.
4. **`tooling/build.sh`**: reconstruye todas las salidas.

### OpenCode como harness

OpenCode concentra el flujo, agentes y permisos. La inferencia se reparte
entre dos suscripciones:

- **GitHub Copilot Pro+** (factura por tokens en AI Credits): solo
  razonamiento que decide — orquestación (GPT-6 Luna), planificación y RCA
  (GPT-6.1 Sol), patrones/seguridad/validación final (Claude Sonnet 5.5) y
  validación crítica + macro-arquitectura (Claude Opus 5.5, en familia
  distinta al planner).
- **OpenCode Go** (topes de uso por modelo): volumen — código (DeepSeek),
  tests (Kimi), planificación estructurada (LongCat/MiMo), revisión y trabajo
  mecánico (GLM/MiMo).

El detalle, la política de privacidad y los modelos bloqueados están en
[`docs/runbooks/opencode-harness.md`](docs/runbooks/opencode-harness.md).

> **Harness recomendado: OpenCode.** Es el único harness con evals ejecutadas
> (12 suites en `evals/cases/`) y el único donde se combinan suscripciones:
> una paga el razonamiento y otra el volumen. Los bindings de ChatGPT y Kiro
> son recomendaciones sin certificar en esos harnesses — si los usas, corre
> primero las evals allí siguiendo
> [`docs/runbooks/evals.md`](docs/runbooks/evals.md).

### Carriles de trabajo

Todo cambio se clasifica al inicio (`master-orchestrator`): `trivial`
(docs/config), `fix` (bug acotado con ODD: outcome + observabilidad),
`feature` (SDD completo) y `workspace` (SDD + enterprise). `fix` exige
aprobación del reviewer **y** Gate 2 humano; cualquier decisión de negocio o
arquitectura escala automáticamente a SDD. Skill:
`outcome-observability-driven`; estados en `core/workflow/states.md`.

## Roles de agentes

| Rol | Agentes |
|-----|---------|
| Workers (obreros) | executor, ui-executor, database-architect, devops-architect, documentation, spec-remediator, functional-tester-agent, git-executor · deprecados: `architect-executor` (reemplazado por carriles ODD), `refactor` (integrado en `executor`) |
| Consultants (consultores) | requirements-analyst, planner, enterprise-architect, solution-architect, test-architect, task-decomposer, context-curator, master-orchestrator |
| Validators (validadores) | spec-validator, enterprise-spec-validator, api-governance-agent, bug-diagnostician, reviewer, security-reviewer, final-validation |
| Guardrails | general |

## Reglas operativas críticas

1. Aislamiento de proyecto: prohibido escribir fuera del repositorio activo.
2. Gates humanos obligatorios: `awaiting-human-plan-approval` y
   `awaiting-human-qa-approval`. Ver `core/workflow/states.md`.
3. Cobertura mínima: 85% en archivos testables.
4. Git exclusivo de `git-executor`: ningún otro agente ejecuta comandos git.
5. Anti-drift: si un agente menciona `model:` o una ruta absoluta `/home/`
   dentro de `core/`, el lint falla.

## Comandos

```bash
tooling/build.sh          # lint + render de adapters + tablas del README
tooling/lint.sh           # valida anti-drift y consistencia
tooling/sync.sh           # instala las salidas generadas (~/.config/opencode, etc.)
tooling/status.sh         # compara instalado vs generado
python3 evals/run.py evals/cases/<suite>.yaml --executor opencode   # evals con modelos reales
python3 tooling/audit_matrix.py   # coherencia agente-fase-skill (debe dar 0)
python3 tooling/validate-states.py [repo]  # estados y gates de shared contexts
```
Ver [`docs/runbooks/evals.md`](docs/runbooks/evals.md) para el flujo de
evaluaciones y [`docs/runbooks/model-change.md`](docs/runbooks/model-change.md)
para cambios de modelo.

## MCPs (Model Context Protocol) en OpenCode

Cinco MCPs extienden las capacidades de los agentes. Se configuran en
`~/.config/opencode/opencode.json` y se instalan con `tooling/sync.sh`.

| MCP | Tipo | Propósito |
|-----|------|-----------|
| **aws-mcp** | Local | Proxy oficial de AWS — expone S3, Lambda, DynamoDB, IAM, CloudWatch, etc. a través de MCP. Usa perfil `merkee` via `AWS_MCP_PROXY_PROFILES`. |
| **playwright** | Local | Control de navegador headless — testing E2E, scraping web, screenshots para `ui-designer` y `functional-tester-agent`. |
| **context7** | Remoto | Documentación actualizada de frameworks/librerías en tiempo real (override de conocimiento interno stale). |
| **github** | Remoto + OAuth | Issues, PRs, repos, search y releases. Requiere autorización OAuth (un solo splash screen). |
| **foundry-jev** | Local | Selector tipado de agente, nivel de razonamiento y aclaración humana mediante Jev. Vercel es el proveedor inicial; Jev oficial queda como alternativa. |

La arquitectura, configuración, umbrales de confianza y procedimiento de
activación están documentados en [`docs/runbooks/jev-routing.md`](docs/runbooks/jev-routing.md).

### Configuración de AWS

Para que un agente IA configure `aws-mcp` en un entorno nuevo:

```bash
# 1. Asegurar que aws-cli esté instalado
aws --version

# 2. Autenticarse (primera vez, abre browser)
aws login --profile merkee

# 3. Verificar que el MCP pueda leer credenciales
aws sts get-caller-identity --profile merkee
```

Las skills `signing-in-to-aws` y `aws-auth` guían el flujo completo (Cognito
user pools, identity pools, tokens, Federación SAML/social). El MCP `aws-mcp`
se encarga del transport y proxy; no necesitas instalar librerías adicionales.

### Visión: modelos con visión nativa (sin MCP local)

Retirado el MCP `foundry-vision` (2026-09-27): todos los agentes que necesitan
ver imágenes usan modelos con visión nativa — `ui-designer` (Claude Sonnet
5.5), `ui-executor` y `functional-tester-agent` (DeepSeek Vision Exp).
`reviewer` (GLM-5.3) no tiene visión: si necesita capturas, delega en
`functional-tester-agent`. Sin costo extra de infraestructura ni VRAM local.

*Estado del plan: ver [PLAN.md](PLAN.md).*

<!-- BEGIN:GENERATED-TABLES -->

## Agentes

### Ciclo de desarrollo de software (27)

| Agente | Rol | Descripción |
|--------|-----|-------------|
| `architect-executor` | Worker (obrero) | Implementa tareas complejas y código de arquitectura local cuando NO existe una especificación SDD completa o formal. ⚠️ DEPRECADO: superseded 2026-09-30 por carriles trivial/fix (odd-card) — ejecucion sin spec eliminada |
| `database-architect` | Worker (obrero) | Diseña y valida esquemas de bases de datos relacionales, migraciones Flyway/Liquibase, índices, modelos DTO/Entidad y estrategias de migración sin inactividad (Zero-Downtime DB Migrations). |
| `devops-architect` | Worker (obrero) | Especialista en Infraestructura como Codigo, Docker, CI/CD y Observabilidad. |
| `documentation` | Worker (obrero) | Creates project documentation, README content, API docs, deployment notes, diagrams, and functional documentation. |
| `executor` | Worker (obrero) | Implementa código a partir de especificaciones SDD aprobadas y descomposiciones de tareas. |
| `git-executor` | Worker (obrero) | Agente exclusivo para operaciones de control de versiones con Git (ramas, commits, checkout, merges, push). |
| `refactor` | Worker (obrero) | Refactors implemented code for maintainability, readability, modularity, and consistency without changing behavior. ⚠️ DEPRECADO: integrado 2026-09-30 en executor (skills refactor-patterns, refactor-hexagonal-bridge) |
| `spec-remediator` | Worker (obrero) | Corrige hallazgos de validación de forma iterativa siguiendo `spec-remediation`. |
| `ui-executor` | Worker (obrero) | Implementa la dirección de diseño UI aprobada como componentes reales del stack destino con verificación visual — traduce el artboard elegido 1:1 sin reinterpretarlo y lo valida con gauntlet visual antes de reportar done. |
| `context-curator` | Consultant (consultor) | Filtra y prepara el contexto de alta señal para evitar ruido a los Obreros y gestionar el ciclo de vida del SDD context. |
| `enterprise-architect` | Consultant (consultor) | Define el System Landscape, fronteras de microservicios y flujos globales siguiendo `enterprise-architecture-standard`. |
| `master-orchestrator` | Consultant (consultor) | Agente Maestro y Orquestador Contextual. Mantiene el contexto de todo el proyecto y delega tareas específicas a subagentes especializados. No realiza modificaciones ni ejecuciones de código directas. |
| `planner` | Consultant (consultor) | Planifica proyectos web con Spec Driven Development, decisiones de arquitectura, contratos API, restricciones tecnicas y documentacion base del proyecto. |
| `requirements-analyst` | Consultant (consultor) | Realiza el levantamiento de requerimientos funcionales siguiendo `requirements-gathering`. |
| `solution-architect` | Consultant (consultor) | Elige patrones de diseno siguiendo `design-patterns-standard`. Colabora con `enterprise-architect` para alinear el diseno local con el global. |
| `task-decomposer` | Consultant (consultor) | Breaks validated specs into small, ordered, executable engineering tasks with dependencies and verification steps. |
| `test-architect` | Consultant (consultor) | Diseña y genera pruebas automatizadas, edge cases, checks de integracion y estrategia de validacion para proyectos web. |
| `ui-designer` | Consultant (consultor) | Diseña direcciones visuales de UI como artefactos HTML comparables antes de implementar código — clarifica alcance, genera 3-4 direcciones distintas respetando el design system del repo y espera la decisión humana. |
| `api-governance-agent` | Validator (validador) | Audita contratos OpenAPI para detectar Breaking Changes, verificar compatibilidad hacia atrás (backward compatibility), auditar semver y aplicar linters de API. |
| `bug-diagnostician` | Validator (validador) | Analiza fallos de QA y producción, examina logs, stack traces e inspecciona el grafo de Graphify para generar un Root Cause Analysis (RCA) detallado antes de implementar arreglos. |
| `enterprise-spec-validator` | Validator (validador) | Valida la consistencia global del Solution Workspace, contratos inter-servicios, System Landscape y la deuda técnica global. |
| `final-validation` | Validator (validador) | Performs final production-readiness validation across specs, implementation, tests, security, documentation, and maintainability. |
| `functional-tester-agent` | Validator (validador) | Disena, ejecuta y reporta pruebas funcionales y de interfaz de usuario (UI/E2E) en frontends. |
| `reviewer` | Validator (validador) | Revisa codigo generado para detectar bugs logicos, drift arquitectonico, mantenibilidad, tests faltantes y cumplimiento de specs. |
| `security-reviewer` | Validator (validador) | Reviews web projects for security risks, OWASP issues, auth/authz flaws, sensitive data handling, and secure architecture. |
| `spec-validator` | Validator (validador) | Valida specs SDD contra ambiguedad, inconsistencia, riesgo arquitectonico, restricciones faltantes y readiness de implementacion. |
| `general` | Guardrail | Guardrail para llamadas accidentales al subagente general integrado de la herramienta anfitriona. Bloquea validaciones SDD ejecutadas por el agente equivocado. |

## Skills (76)

### Arquitectura y Metodología

| Skill | Descripción |
|-------|-------------|
| `api-governance-linter` | Reglas de auditoría de contratos OpenAPI 3.0/3.1, detección de Breaking Changes y políticas de versión semántica (SemVer) para el agente api-governance-agent. |
| `design-patterns-standard` | Criterios pragmaticos para aplicar patrones de diseno sin sobreingenieria y respetando boundaries de arquitectura hexagonal. |
| `enterprise-architecture-standard` | Criterios para macro-arquitectura, system landscape, bounded contexts, integraciones, ownership y workspace multi-repos. |
| `hexagonal-architecture` | Implementación de Puertos y Adaptadores (Clean Architecture) con dominio puro, boundaries explícitos, estructura de directorios por tecnología y desacoplamiento total de frameworks. |
| `openapi-first` | Flujo API Design First para mantener specs, OpenAPI, implementación, clientes, tests y copias runtime sincronizados antes de escribir código. |
| `outcome-observability-driven` | Carriles ligeros trivial y fix que complementan SDD — Outcome-Driven (resultado verificable) + Observability-Driven (reproducción y señales) con odd-card de una página, límites explícitos y escalamiento obligatorio a SDD ante cualquier decisión de negocio o arquitectura. |
| `project-context-files` | Patrón de archivos de contexto jerárquicos (.md) heredado de Claude Code/AGENTS.md — cómo estructurar memoria por capas en repositorios activos para que los agentes hereden contexto correcto sin inflar prompts. |
| `refactor-hexagonal-bridge` | Skill especializada para la transición de sistemas monolíticos o con lógica dispersa hacia Arquitectura Hexagonal de forma segura. |
| `refactor-patterns` | Patrones de refactorización segura. |
| `repository-dto-patterns` | Patrones para separar modelos de dominio, DTOs de transporte, entidades de persistencia, repositories/adapters y mappings entre capas. |
| `requirements-gathering` | Estándares y estructura para el levantamiento de requerimientos funcionales antes de planificación SDD. |
| `spec-driven-development` | Ciclo de vida de desarrollo basado en especificaciones (Master Specs e Incrementos). Asegura que el código siempre esté alineado con la documentación, ya sea en proyectos nuevos, nuevas funcionalidades o modificaciones. |
| `spec-remediation` | Procedimiento para la corrección iterativa de hallazgos en especificaciones SDD. |

### Backend y Lenguajes

| Skill | Descripción |
|-------|-------------|
| `fastapi-rest-error-response-standards` | Estandariza respuestas HTTP de error en FastAPI con exception handlers globales, Pydantic v2, codigos estables, seguridad, OpenAPI y tests. |
| `fastapi-stack` | Estandares y mejores practicas para FastAPI alineados con Arquitectura Hexagonal, OpenAPI, Pydantic v2 y separation of concerns. |
| `golang-stack` | Estándares de calidad, estructura del proyecto y mejores prácticas de diseño para aplicaciones de Backend en Go / Golang. |
| `java-stack` |  |
| `jpa-stack` | Convenciones para Jakarta Persistence/Hibernate en Spring Boot: entidades, repositories, auditoria, soft delete, transacciones, locking y performance. |
| `kotlin-stack` |  |
| `nodejs-stack` |  |
| `openapi-standard` | Convenciones concretas para escribir contratos OpenAPI: version, estructura, schemas, parametros, seguridad, errores, ejemplos y validacion. |
| `python-stack` | Estándares y mejores prácticas para el desarrollo con Python 2026. |
| `restful-standard` | Convenciones REST para recursos, metodos HTTP, status codes, paginacion, filtros, versionado, compatibilidad, seguridad e idempotencia. |
| `spring-cloud-gateway` | Estándares y mejores prácticas para la implementación de API Gateways con Spring Cloud Gateway. |
| `springboot-java-rest-error-response-standards` | Estandariza respuestas HTTP de error en APIs Spring Boot Java con RestControllerAdvice, ApiErrorResponse, codigos estables, seguridad, OpenAPI y tests. |
| `springboot-kotlin-rest-error-response-standards` | Estandariza respuestas HTTP de error en APIs Spring Boot Kotlin con RestControllerAdvice, data classes, codigos estables, seguridad, OpenAPI y tests. |
| `springboot-stack` | Convenciones de Spring Boot 2026 (Virtual Threads, Records, Pattern Matching) y estándares de pruebas JaCoCo. |

### Datos y Mensajería

| Skill | Descripción |
|-------|-------------|
| `amazon-sqs-standard` | Mejores prácticas para Amazon SQS (Visibility Timeout, DLQ, Batching, FIFO). |
| `flyway-migrations` | Gestión de esquemas de base de datos mediante migraciones incrementales con Flyway. Compatible con PostgreSQL, MySQL, Oracle y SQL Server. |
| `kafka-standard` | Mejores prácticas para Apache Kafka (Particiones, Idempotencia, Schema Registry, EOS). |
| `mysql-standard` | Estándares y mejores prácticas para el diseño y gestión de bases de datos MySQL. |
| `oracle-standard` | Estándares y mejores prácticas para el diseño y gestión de bases de datos Oracle. |
| `postgresql-standard` | Estándares y mejores prácticas para el diseño y gestión de bases de datos PostgreSQL. |
| `rabbitmq-standard` | Mejores prácticas para RabbitMQ en Arquitectura Hexagonal (Direct/Topic Exchanges, DLQ, Outbox, Idempotencia). |
| `sqlserver-standard` | Estándares y mejores prácticas para el diseño y gestión de bases de datos SQL Server. |
| `zero-downtime-migrations` | Patrones de evolución de esquemas relacionales sin tiempo de inactividad utilizando el patrón Expand/Contract, índices en segundo plano y migraciones seguras en Flyway. |

### Frontend y Diseño UI/UX

| Skill | Descripción |
|-------|-------------|
| `accessibility-standard` | Auditoría y diseño accesible WCAG 2.2 AA — criterios completos con verificación práctica (teclado, contraste, ARIA, targets táctiles, formularios), herramientas automatizadas y clasificación de severidad para bloquear releases. |
| `angular-stack` |  |
| `design-systems` | Descubrimiento, uso y validación de design systems en el código — extraer tokens y componentes existentes para que los diseños nuevos nazcan consistentes con la UI real del producto. |
| `design-to-code` | Traducción fiel de un artefacto de diseño aprobado (HTML en docs/designs/) a componentes reales del stack destino, con verificación visual automatizada — el puente entre la dirección elegida y el ui-executor. |
| `frontend-architecture` | Arquitectura limpia para React y Angular. |
| `minimalist-ui` | Clean editorial-style interfaces. Warm monochrome palette, typographic contrast, flat bento grids, muted pastels. No gradients, no heavy shadows. |
| `react-stack` |  |
| `ui-design-exploration` | Protocolo de exploración visual estilo canvas — genera 3-4 direcciones de diseño realmente distintas como artefactos HTML autocontenidos antes de escribir código de producción, con preguntas de clarificación, índice comparativo y decisión humana obligatoria. |
| `ux-heuristics` | Heurísticas de usabilidad aplicadas — Nielsen accionable, estados de interacción obligatorios, UX writing, formularios y accesibilidad rápida para revisar o diseñar cualquier interfaz. |

### Seguridad y Calidad

| Skill | Descripción |
|-------|-------------|
| `bug-fixing-workflow` | Protocolo riguroso para la resolución de errores. Prioriza la reproducción empírica y la integridad arquitectónica sobre los parches rápidos. |
| `code-quality-and-sonarqube` | Estándares de análisis estático de código, SonarQube, linters (Ruff, SpotBugs, golangci-lint, ESLint), pruebas de mutación diferencial y análisis CRAP por diff con el bucle de auto-verificación ./verify-code.sh. |
| `code-review-checklist` | Lista de verificación para revisión de código orientada a bugs, regresiones, drift arquitectónico, seguridad, performance, tests y cumplimiento de specs. |
| `docker-standard` |  |
| `functional-testing-standard` | Estándares y flujo de trabajo para el diseño, ejecución y corrección de pruebas funcionales en Frontends usando Puppeteer MCP o frameworks locales del workspace. |
| `keycloak-standard` | Estándares y mejores prácticas para la configuración y gestión de identidad con Keycloak. |
| `observability-standard` |  |
| `performance-testing-k6` | Estándares de pruebas de carga, estrés y latencia de APIs con k6, verificación de SLAs de rendimiento (p95 < 200ms) y reportes de degradación. |
| `pre-flight-check` | Validación técnica obligatoria antes de cerrar tareas, aprobar incrementos o realizar commits. Exige evidencia real de filesystem, build, tests, cobertura, migraciones y servicios cuando aplique. |
| `root-cause-analysis` | Protocolo de investigación no destructiva, triage de logs, análisis de causa raíz (RCA) y formulación de hipótesis para el agente bug-diagnostician. |
| `security-standards` | Estándares de seguridad para aplicaciones Spring Boot y Frontend. Usar para JWT, OAuth2/OIDC, Keycloak, RBAC, prevención de vulnerabilidades y gestión de identidad. |
| `testing-strategy` | Estrategia unificada de pruebas, metodología TDD (Red-Green-Refactor), pruebas de concurrencia, tests de arquitectura, cobertura mínima, definición operativa de módulo testable y política de mutación diferencial para múltiples stacks. |

### Orquestación y Documentación

| Skill | Descripción |
|-------|-------------|
| `context-curation` | Estrategia de selección de contexto relevante para cada agente. |
| `context-pinning` | Gestión de archivos críticos para mantener la integridad arquitectónica y el diseño del sistema. Asegura que los agentes siempre lean la Master Spec y los contratos vigentes. |
| `documentation-lifecycle` | Gestión del ciclo de vida de la documentación técnica. Automatiza la consolidación de incrementos en la Master Spec para mantener una fuente de verdad única. |
| `documentation-standards` | Estándares de documentación técnica y READMEs. |
| `eval-ops-agent-benchmarks` | Protocolo de evaluación automatizada y pruebas de regresión para agentes de IA cuando se actualizan sus prompts, modelos o reglas en config-ai. |
| `git-ops` | Gestión profesional del ciclo de vida de Git y GitHub. Automatiza la creación de ramas, commits semánticos y Pull Requests siguiendo estándares de la industria y el flujo SDD. |
| `graphify` | "Use for any question about a codebase, its architecture, file relationships, or project content — especially when graphify-out/ exists, where the question should be treated as a graphify query first. Turns any input (code, docs, papers, images, videos) into a persistent knowledge graph with god nodes, community detection, and query/path/explain tools." |
| `workspace-coordination` | Coordinación técnica ascendente y descendente entre el Solution Workspace y proyectos locales, incluyendo la gestión y visibilidad de la deuda técnica. |

### Sistema Local (ambxst / Linux)

| Skill | Descripción |
|-------|-------------|
| `ambxst-packaging` | Empaquetado e instalación de ambxst — install.sh multi-distro (Arch/Fedora/NixOS), flake.nix, dependencias Quickshell/Hyprland y flujo de release del fork personal. |
| `ambxst-plugins` | Cómo extender ambxst con nuevas features/plugin-modules end-to-end (clave de config, servicio, UI, integración en notch/bar/dashboard) siguiendo el patrón de módulos existentes. |
| `ambxst-shell-dev` | Desarrollo de módulos y features en el shell ambxst (Quickshell/QML sobre Wayland). Arquitectura, convenciones, anti-patrones y flujo de trabajo para modificar el fork personal. |
| `ambxst-theming` | Sistema de theming de ambxst — generación de paleta con matugen desde wallpaper, colores reactivos del shell y sincronización en vivo con GTK (adw-gtk3), Qt/KDE (kdeglobals + D-Bus) y Kitty. |
| `linux-dev` | Estándares de programación sobre Linux — bash estricto, servicios systemd, D-Bus, jerarquía de archivos, permisos y empaquetado básico. Para scripts, daemons de usuario e integraciones de escritorio Wayland/X11. |

### Otras

| Skill | Descripción |
|-------|-------------|
| `documentation-reconciliation` | "Interpretar documentación de proyectos, distinguir estado actual de planes e histórico y resolver contradicciones entre README, specs, código y tests con evidencia." |
| `jev-routing` | Enrutamiento tipado mediante Jev para seleccionar agente, nivel de razonamiento y necesidad de intervención humana sin delegar permisos ni ejecución a Jev. |
| `n8n-stack` |  |
| `planning-context-pack` | Prepara un contexto de planificación persistente, mínimo y trazable desde specs y código para que un modelo de razonamiento no relea el repositorio completo. |
| `project-context-navigation` | "Orientarse rápidamente en un proyecto desconocido para ubicar su estructura, fuentes de verdad, flujo de trabajo y archivos relevantes antes de responder o editar." |
| `secret-scanning` | Escaneo obligatorio de secretos con Gitleaks para agentes que escriben, validan o versionan artefactos del repositorio. |


### Skills para ChatGPT Desktop

Estas skills son específicas de ChatGPT Desktop/Codex y no se instalan en
OpenCode. Las skills desktop-only se mantienen fuera de `core/skills` para
evitar que el adapter de OpenCode las copie a su configuración.

| Skill | Descripción |
|-------|-------------|
| `agent-foundry-reader` | Analiza repositorios construidos con la filosofía Agent Foundry y explica su arquitectura, agentes, skills, workflow SDD, gates, handoffs y drift en modo estrictamente solo lectura. Exclusiva para ChatGPT Desktop; no usar para OpenCode ni para modificar proyectos. |
| `documentation-reconciliation` | "Interpretar documentación de proyectos, distinguir estado actual de planes e histórico y resolver contradicciones entre README, specs, código y tests con evidencia." |
| `project-context-navigation` | "Orientarse rápidamente en un proyecto desconocido para ubicar su estructura, fuentes de verdad, flujo de trabajo y archivos relevantes antes de responder o editar." |

La skill `agent-foundry-reader` se instala mediante
`tooling/sync-chatgpt.sh`. Consulta el [runbook de skills para ChatGPT Desktop]
(docs/runbooks/chatgpt-desktop-skills.md) para el flujo completo.

## Modelos por herramienta

### OpenCode — bindings activos

| Agente | Modelo de ejecución |
|--------|--------------------|
| `api-governance-agent` | opencode-go/mimo-v2.6-pro |
| `bug-diagnostician` | github-copilot/gpt-6.1-sol |
| `context-curator` | opencode-go/mimo-v2.6-flash |
| `database-architect` | opencode-go/deepseek-v4-pro |
| `devops-architect` | opencode-go/deepseek-v4.1-flash |
| `documentation` | opencode-go/mimo-v2.6-flash |
| `enterprise-architect` | github-copilot/claude-opus-5.5 |
| `enterprise-spec-validator` | opencode-go/kimi-k3 |
| `executor` | opencode-go/deepseek-v4.1-flash |
| `final-validation` | github-copilot/claude-sonnet-5.5 |
| `functional-tester-agent` | opencode-go/deepseek-v4-flash-vision-exp |
| `git-executor` | opencode-go/mimo-v2.6-flash |
| `master-orchestrator` | github-copilot/gpt-6-luna |
| `planner` | github-copilot/gpt-6.1-sol |
| `reviewer` | opencode-go/glm-5.3 |
| `security-reviewer` | github-copilot/claude-sonnet-5.5 |
| `solution-architect` | github-copilot/claude-sonnet-5.5 |
| `spec-remediator` | opencode-go/mimo-v2.6-pro |
| `spec-validator` | github-copilot/claude-opus-5.5 |
| `task-decomposer` | opencode-go/mimo-v2.6-pro |
| `test-architect` | opencode-go/kimi-k2.7-code |
| `ui-designer` | github-copilot/claude-sonnet-5.5 |
| `ui-executor` | opencode-go/deepseek-v4-flash-vision-exp |

### ChatGPT (Codex CLI) — bindings recomendados (sin evals en este harness)

| Agente | Modelo de ejecución |
|--------|--------------------|
| `api-governance-agent` | `gpt-5.6-sol` |
| `architect-executor` | `gpt-5.6-terra` |
| `bug-diagnostician` | `gpt-5.6-terra` |
| `context-curator` | `gpt-5.6-luna` |
| `database-architect` | `gpt-5.6-terra` |
| `devops-architect` | `gpt-5.6-luna` |
| `documentation` | `gpt-5.6-luna` |
| `enterprise-architect` | `gpt-5.6-sol` |
| `enterprise-spec-validator` | `gpt-5.6-sol` |
| `executor` | `gpt-5.6-terra` |
| `final-validation` | `gpt-5.6-luna` |
| `functional-tester-agent` | `gpt-5.6-luna` |
| `general` | `gpt-5.6-luna` |
| `git-executor` | `gpt-5.6-luna` |
| `master-orchestrator` | `gpt-5.6-luna` |
| `planner` | `gpt-5.6-sol` |
| `refactor` | `gpt-5.6-terra` |
| `requirements-analyst` | `gpt-5.6-luna` |
| `reviewer` | `gpt-5.6-luna` |
| `security-reviewer` | `gpt-5.6-luna` |
| `solution-architect` | `gpt-5.6-sol` |
| `spec-remediator` | `gpt-5.6-luna` |
| `spec-validator` | `gpt-5.6-sol` |
| `task-decomposer` | `gpt-5.6-sol` |
| `test-architect` | `gpt-5.6-luna` |
| `ui-designer` | `gpt-5.6-sol` |
| `ui-executor` | `gpt-5.6-luna` |

### Kiro — bindings recomendados (sin evals en este harness)

| Agente | Modelo de ejecución |
|--------|--------------------|
| `api-governance-agent` | `claude-sonnet-5` |
| `architect-executor` | `claude-sonnet-5` |
| `bug-diagnostician` | `claude-sonnet-5` |
| `context-curator` | `claude-haiku-4.5` |
| `database-architect` | `claude-sonnet-5` |
| `devops-architect` | `claude-haiku-4.5` |
| `documentation` | `claude-haiku-4.5` |
| `enterprise-architect` | `claude-sonnet-5` |
| `enterprise-spec-validator` | `claude-opus-5` |
| `executor` | `claude-sonnet-5` |
| `final-validation` | `claude-haiku-4.5` |
| `functional-tester-agent` | `claude-sonnet-5` |
| `general` | `claude-haiku-4.5` |
| `git-executor` | `claude-haiku-4.5` |
| `master-orchestrator` | `claude-haiku-4.5` |
| `planner` | `claude-sonnet-5` |
| `refactor` | `claude-sonnet-5` |
| `requirements-analyst` | `claude-haiku-4.5` |
| `reviewer` | `claude-haiku-4.5` |
| `security-reviewer` | `claude-haiku-4.5` |
| `solution-architect` | `claude-sonnet-5` |
| `spec-remediator` | `claude-haiku-4.5` |
| `spec-validator` | `claude-opus-5` |
| `task-decomposer` | `claude-sonnet-5` |
| `test-architect` | `claude-haiku-4.5` |
| `ui-designer` | `claude-sonnet-5` |
| `ui-executor` | `claude-sonnet-5` |

<!-- END:GENERATED-TABLES -->
