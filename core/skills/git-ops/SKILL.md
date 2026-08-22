---
name: git-ops
description: Gestión profesional del ciclo de vida de Git y GitHub. Automatiza la creación de ramas, commits semánticos y Pull Requests siguiendo estándares de la industria y el flujo SDD.
---

# Git Ops Skill

Esta skill permite a los agentes gestionar el flujo de trabajo de Git de forma autónoma y profesional, asegurando consistencia en los mensajes de commit y la estructura del repositorio.

## 1. Convenciones de Ramas (Branching)

Antes de realizar cambios, el agente debe asegurarse de estar en la rama correcta o crear una nueva si la tarea lo requiere.

- **Formato:** `tipo/descripcion-breve`
- **Tipos:**
  - `feature/`: Nuevas funcionalidades o mejoras.
  - `fix/`: Corrección de errores.
  - `docs/`: Cambios solo en documentación.
  - `refactor/`: Cambios en el código que no añaden funcionalidad ni corrigen errores.
  - `chore/`: Tareas de mantenimiento (actualización de dependencias, configs).

## 2. Mensajes de Commit (Conventional Commits)

Los mensajes deben ser claros y seguir el estándar `tipo(scope): descripcion`.

- **Tipos:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.
- **Scope:** Debe ser exactamente el identificador del incremento activo (ej. `user-auth`, `invoice-export`) o el sub-módulo técnico si el incremento abarca múltiples áreas. Prohibido usar marcadores genéricos.
- **Descripción:** En minúsculas, tiempo presente, máximo 50 caracteres.

**Ejemplo:** `feat(user-auth): implement JWT token rotation`

## 3. Flujo de Trabajo Operativo

El agente debe seguir este orden estrictamente:

### Paso A: Verificación (Pre-commit & Gitleaks Secret Shield)
Nunca realizar un commit si el código contiene secretos o no ha sido verificado.
- **Escaneo de Secretos (Gitleaks)**: Ejecutar `gitleaks detect --staged --verbose` para asegurar que ningún token, clave privada o API Key esté en staging.
- **Hooks de Git Automatizados**: Instalar el pre-commit hook ejecutable `.git/hooks/pre-commit` que ejecuta `gitleaks` y los linters ultrarrápidos (`ruff`, `golangci-lint`, `spotbugs`, `pnpm run lint`).
- **Tests Unitarios**: Ejecutar tests con el gestor del stack: `pnpm test`, `./mvnw test`, `pytest`, `go test ./...`.
- En proyectos JavaScript/TypeScript, usar `pnpm`; si existe `package-lock.json`, proponer migración a `pnpm-lock.yaml`.

### Paso B: Preparación de Cambios
1. Identificar archivos modificados relacionados estrictamente con la tarea.
2. Hacer `git add` de los archivos específicos. Evitar `git add .` si hay cambios no relacionados.

### Paso C: Commit Semántico
Generar el mensaje basado en el análisis de los cambios realizados. Si hay dudas sobre el scope, usar el nombre del directorio principal afectado.

### Paso D: Publicación y PR (GitHub)
Si la tarea incluye el cierre de la implementación:
1. **Verificación de Gate Humano:** Antes de empujar a ramas estables (`develop`, `qa`, `master`) o de abrir un PR, validar que el Shared Context contenga el encabezado explícito `## Human QA Approval: approved_by_user`. Si falta, detener la operación y reportar bloqueo.
2. **Git Hook Guard:** Verificar que el pre-push hook local de Git esté instalado en el repositorio activo (`.git/hooks/pre-push` copiado desde `pre-push-hook-template.sh` y con permisos de ejecución). Queda prohibido hacer bypass (`--no-verify`) o alterar el hook.
3. `git push origin <branch-name>`.
4. Utilizar el MCP de GitHub (`github_create_pull_request`) para abrir el PR.
5. El título del PR debe ser el mismo que el del commit principal.
6. El cuerpo del PR debe incluir un resumen de los cambios y mencionar si cierra algún issue (ej. `Closes #123`).


## 4. Integración con SDD

- **Planner/Task Decomposer:** Deben indicar si la tarea requiere una nueva rama.
- **Executor:** Debe realizar commits atómicos por cada tarea completada del desglose.
- **Final Validation:** Debe confirmar que el PR ha sido creado correctamente antes de dar la sesión por concluida.

## 5. Comandos de Referencia Rápida

- Crear rama: `git checkout -b feature/nueva-feat`
- Ver cambios: `git status` y `git diff --cached`
- Commit: `git commit -m "feat(scope): desc"`
- Push: `git push origin HEAD`
