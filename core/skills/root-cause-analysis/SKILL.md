---
name: root-cause-analysis
description: Protocolo de investigación no destructiva, triage de logs, análisis de causa raíz (RCA) y formulación de hipótesis para el agente bug-diagnostician.
---

# Root Cause Analysis (RCA) & Triage Protocol

Guía operativa para el agente `bug-diagnostician` para analizar fallos en QA y producción de forma científica, rigurosa y no destructiva (sin modificar código directamente).

---

## 1. El Proceso de Diagnóstico en 4 Pasos

```
1. Extracción de Evidencia ➔ 2. Aislamiento del Componente ➔ 3. Formulación de Hipótesis ➔ 4. Reporte RCA
```

### Paso 1: Extracción de Evidencia (Log & Trace Parsing)
- Capturar el **stack trace completo** no truncado de la excepción.
- Extraer el ID de traza distribuida (`traceId`, `spanId`) si OpenTelemetry está configurado.
- Inspeccionar la carga útil (payload de request) que desencadenó el fallo y la respuesta HTTP/código de error.

### Paso 2: Aislamiento del Componente y Consulta de Grafo
- Utilizar `graphify query` para rastrear las dependencias del módulo fallido hacia atrás (Controlador ➔ UseCase ➔ Servicio ➔ Entidad ➔ Base de Datos).
- Identificar si el fallo ocurrió en la capa de **Dominio** (regla de negocio no contemplada), **Aplicación** (idempotencia/transacción), **Infraestructura** (timeout/DB lock) o **Integración** (contrato externo roto).

### Paso 3: Formulación de Hipótesis y Reproducción
- Formular la hipótesis exacta del fallo: *"El fallo ocurre porque la entidad X no maneja el estado NULL en la propiedad Y cuando el proveedor Z responde HTTP 422"*.
- Diseñar los pasos mínimos y deterministas para reproducir el bug mediante un test unitario o de integración fallido (Fase RED de TDD).

### Paso 4: Emisión del Reporte de RCA
Generar el reporte de diagnóstico estructurado en:
`docs/specs/.working/<increment-name>-bug-rca.md`

```markdown
# Reporte de Análisis de Causa Raíz (RCA)

**Incidente / Bug:** [Nombre o ID del error]
**Fecha:** [AAAA-MM-DD HH:MM]
**Diagnosticador:** bug-diagnostician

---

## 1. Evidencia Técnica
- **Excepción:** `com.empresa.domain.exception.EntityNotFoundException`
- **Componente Afectado:** `src/main/java/.../OrderUseCase.java:L45`
- **Payload Gatillo:** `{ "orderId": null, ... }`

---

## 2. Causa Raíz Confirmada
Explicación técnica detallada de la razón fundamental del fallo.

---

## 3. Estrategia de Solución Recomendada
- Pasos de solución sugeridos sin modificar código.
- **Agente Destino Sugerido:** [executor (fix mecánico) / planner (drift de spec) / devops-architect (infraestructura)]
```
