---
name: code-quality-and-sonarqube
description: Estándares de análisis estático de código, SonarQube, linters (Ruff, SpotBugs, golangci-lint, ESLint) y pruebas de mutación (PITest) con el bucle de auto-verificación ./verify-code.sh.
---

# Code Quality, SonarQube & Auto-Verification Protocol

Guía mandatoria para el agente `final-validation` y los ejecutores para auditar la calidad estática del código, la ausencia de deuda técnica y la ejecución del bucle de auto-verificación `./verify-code.sh`.

---

## 1. Servidor SonarQube Local & SonarScanner

SonarQube Community Edition se ejecuta localmente en la máquina:
- **URL Base**: `http://localhost:9000`
- **Credenciales Iniciales**: `admin` / `admin`

### Archivo `sonar-project.properties` (En la Raíz de Cada Proyecto)

```properties
sonar.projectKey=nombre-del-proyecto
sonar.projectName=Nombre del Proyecto
sonar.projectVersion=1.0.0

sonar.sources=src
sonar.tests=tests,src/test
sonar.language=java

# Archivos de Cobertura de Tests
sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml,build/reports/jacoco/test/jacocoTestReport.xml
sonar.python.coverage.reportPaths=coverage.xml
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Exclusiones
sonar.exclusions=**/DTO.java,**/dtos.py,**/config/**
```

---

## 2. Linters Estrictos por Stack Tecnológico

| Stack | Linter / Formatter | Comando de Ejecución |
|---|---|---|
| **Python (FastAPI)** | Ruff + MyPy | `ruff check .` && `mypy src` |
| **Java / Kotlin (Spring)** | SpotBugs + Checkstyle | `./mvnw spotbugs:check` / `./gradlew spotbugsMain` |
| **Go (Golang)** | `golangci-lint` | `golangci-lint run ./...` |
| **Node.js / TypeScript** | ESLint + Prettier | `pnpm run lint` && `tsc --noEmit` |

---

## 3. Pruebas de Mutación (Mutation Testing)

Las pruebas de mutación alteran intencionalmente el código de producción para certificar que las aserciones de los tests son fuertes (*mutant killing*).

- **Java/Kotlin**: `./gradlew pitest` / `./mvnw pitest:mutationAnalysis` (PITest)
- **Python**: `mutmut run` (Mutmut)
- **TypeScript**: `stryker run` (Stryker)

---

## 4. Script de Auto-Verificación Unificado (`./verify-code.sh`)

Todo proyecto debe contar con la plantilla del script ejecutable `./verify-code.sh` que ejecuta secuencialmente:

```bash
#!/usr/bin/env bash
set -e

echo "=== 1. Pruebas Unitarias e Integración (Testcontainers) ==="
./mvnw test || pytest || pnpm test

echo "=== 2. Pruebas de Arquitectura Hexagonal (ArchUnit) ==="
./mvnw test -Dtest=*ArchitectureTest || pytest tests/test_architecture.py || true

echo "=== 3. Auditoría Estática de Código (Linters) ==="
golangci-lint run ./... || ruff check . || ./mvnw spotbugs:check || pnpm run lint

echo "=== 4. Escaneo de Seguridad y Dependencias ==="
govulncheck ./... || pip-audit || pnpm audit || true

echo "=== 5. Análisis de SonarScanner ==="
if command -v sonar-scanner >/dev/null 2>&1; then
    sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.token=${SONAR_TOKEN:-admin}
fi

echo "✅ VERIFICACIÓN DE CÓDIGO COMPLETADA CON ÉXITO"
```

---

## 5. Regla de Bloqueo para `final-validation`

- 🚫 **Bloquear**: Si el script `./verify-code.sh` o su equivalente retorna código de salida distinto de `0`.
- 🚫 **Bloquear**: Si SonarQube reporta vulnerabilidades de severidad `HIGH` / `CRITICAL` o duplicación de código > 3%.
- 🚫 **Bloquear**: Si el umbral de cobertura por archivo testable cae por debajo del 85%.
