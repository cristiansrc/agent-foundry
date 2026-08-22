---
name: eval-ops-agent-benchmarks
description: Protocolo de evaluación automatizada y pruebas de regresión para agentes de IA cuando se actualizan sus prompts, modelos o reglas en config-ai.
---

# EvalOps: Framework de Evaluación de Agentes & Benchmarks

Guía metodológica para auditar la precisión, estructura JSON, tasa de alucinaciones y cumplimiento de normas de los agentes de IA en `config-ai` tras realizar cambios en sus definiciones o modelos.

---

## 1. El Principio de EvalOps

Cualquier cambio en el modelo o prompt de un agente (ej. migrar `planner` de un modelo a otro en el perfil de ejecución) debe certificarse ejecutando una suite de prueba contra **Specs Canónicas de Referencia** (*Gold Standard Specs*).

---

## 2. Los 4 Criterios de Evaluación por Agente

```mermaid
graph TD
    A[Generación de Agente] ➔ B{1. Compliance de Esquema JSON / YAML}
    B ➔|OK| C{2. Precisión de Reglas de Negocio}
    C ➔|OK| D{3. Cero Alucinación de Rutas / Comandos}
    D ➔|OK| E{4. Tiempo de Respuesta & Costo de Tokens}
```

1. **Esquema & Sintaxis (Schema Compliance)**: El output debe respetar estrictamente los headings de Markdown o campos JSON definidos en el prompt del agente.
2. **Precisión Técnica**: El agente no debe aprobar artefactos incompletos ni omitir violaciones de contrato.
3. **Cero Alucinación**: El agente no debe inventar rutas de archivos inexistentes ni paquetes no declarados en el workspace.
4. **Eficiencia**: Monitorear el consumo de tokens y latencia de respuesta.

---

## 3. Dataset Canónico de Prueba (*Gold Standard Suite*)

En `tests/eval-ops/gold-standards/` se mantienen 3 especificaciones de referencia:
- `spec-good-sample.md`: Spec 100% correcta (debe ser aprobada con veredicto `ready`).
- `spec-bad-architecture.md`: Spec con violación de frontera hexagonal (debe ser rechazada con veredicto `not_ready`).
- `spec-missing-contract.md`: Spec sin schema OpenAPI (debe marcar hallazgo de contrato faltante).

---

## 4. Ejecución del Benchmark

```bash
# Script de evaluación de regresión de agentes (--model toma el valor del perfil de ejecución activo)
python3 tests/eval-ops/run_benchmarks.py --agent spec-validator --model <modelo-del-perfil>
```
