---
name: performance-testing-k6
description: Estándares de pruebas de carga, estrés y latencia de APIs con k6, verificación de SLAs de rendimiento (p95 < 200ms) y reportes de degradación.
---

# Performance & Load Testing Standard (k6)

Guía operativa para el agente `test-architect` e implementadores para diseñar, ejecutar y auditar pruebas de rendimiento y carga en APIs REST y microservicios utilizando **k6**.

---

## 1. Umbrales Mandatorios de SLA de Rendimiento

Todo endpoint de producción debe cumplir los siguientes Criterios de Aceptación de Rendimiento:
- **Latencia Percentil 95 (p95)**: **< 200ms**.
- **Latencia Percentil 99 (p99)**: **< 500ms**.
- **Tasa de Errores HTTP (4xx / 5xx)**: **< 1%**.
- **Rendimiento Mínimo (Throughput)**: 100 peticiones sostenidas por segundo (RPS) en escenarios de carga estándar.

---

## 2. Tipos de Pruebas de Carga en k6

### A. Smoke Test (Prueba Humo de Carga)
Verifica que el script y los endpoints funcionan con 1 o 2 usuarios virtuales (VUs).
```javascript
// tests/performance/smoke.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '10s',
  thresholds: {
    http_req_duration: ['p(95)<200'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('http://localhost:8080/api/v1/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

### B. Load Test (Prueba de Carga Sostenida)
Evalúa el comportamiento bajo carga esperada sostenida.
```javascript
// tests/performance/load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp-up a 50 usuarios
    { duration: '1m',  target: 50 },  // Mantener 50 usuarios
    { duration: '15s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const payload = JSON.stringify({ name: 'Test' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post('http://localhost:8080/api/v1/orders', payload, params);
  check(res, { 'created 201': (r) => r.status === 201 });
  sleep(0.5);
}
```

---

## 3. Comando de Ejecución y Reportes

```bash
# Ejecutar prueba de rendimiento en local
k6 run tests/performance/load.js

# Exportar métricas en JSON para auditoría
k6 run --summary-export=graphify-out/k6-summary.json tests/performance/load.js
```

---

## 4. Regla de Bloqueo

- 🚫 **Bloquear**: Si en la prueba de carga sostenida `p(95)` supera los 200ms o la tasa de fallo de HTTP supera el 1%.
