---
name: hyprmind-workspace-manager
description: Procedimientos para abrir documentos e IDEs en el escritorio del usuario.
---

# Skill: hyprmind-workspace-manager

## 🎯 Objetivo
Definir los procedimientos exactos sobre **CÓMO** abrir archivos, revisar documentos y levantar Entornos de Desarrollo Integrados (IDEs) en el sistema operativo Hyprland del usuario.

## 🛠️ Procedimientos de Ejecución

### 1. Revisión de Documentos y Archivos Sueltos (Markdown/Texto)
Si el usuario necesita revisar o leer un archivo de texto o un documento Markdown (`.md`):
*   **Comando a ejecutar:** `kitty -e glow <ruta-absoluta-del-archivo>`
*   **Lógica:** Esto abrirá una nueva instancia de la terminal `kitty` corriendo el visualizador `glow` para que el usuario lea el documento cómodamente.

### 2. Apertura de Proyectos e IDEs
Cuando el usuario indique que quiere trabajar en un proyecto o que debes mostrarle un proyecto completo, debes determinar el lenguaje principal del proyecto y ejecutar el comando asociado en segundo plano:

| Lenguaje / Entorno | Comando de Terminal a Ejecutar |
| :--- | :--- |
| **Java / Kotlin** | `idea <ruta-del-proyecto> &` (IntelliJ IDEA) |
| **Python** | `pycharm <ruta-del-proyecto> &` (PyCharm) |
| **Go / Golang** | `goland <ruta-del-proyecto> &` (GoLand) |
| **JavaScript / TypeScript / Otros** | `code <ruta-del-proyecto> &` (VS Code) |

### 3. Reglas de Validación
*   Asegúrate siempre de usar rutas absolutas para evitar errores de directorio de trabajo (CWD).
*   Si no estás seguro del lenguaje del proyecto, pregúntale al usuario o inspecciona rápidamente los archivos del directorio (ej. buscar `pom.xml`, `package.json`, `main.go`).
