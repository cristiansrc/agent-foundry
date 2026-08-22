---
name: ambxst-shell-dev
description: Desarrollo de módulos y features en el shell ambxst (Quickshell/QML sobre Wayland). Arquitectura, convenciones, anti-patrones y flujo de trabajo para modificar el fork personal.
---

# Skill: ambxst Shell Development

Guía para desarrollar en el fork personal de ambxst (`~/.local/src/ambxst`,
repositorio `cristiansrc/ambxst`). Shell Wayland construido con Quickshell
(QtQuick/QML) con panel unificado (bar, dock, notch), dashboard, lockscreen,
widgets de escritorio y sistema de notificaciones.

## Antes de tocar código

1. Lee el `AGENTS.md` de la raíz Y el de la carpeta que vas a modificar
   (`config/`, `modules/services/`, `modules/bar/`, etc. tienen los suyos).
2. Identifica el tipo de cambio: UI (modules/), backend (services/scripts),
   configuración (config/) o empaquetado (nix/, install.sh).

## Arquitectura esencial

| Pieza | Ubicación | Rol |
|-------|-----------|-----|
| Entry point | `shell.qml` | `ShellRoot` → `Variants` por pantalla; init de servicios |
| Config | `config/Config.qml` | >3100 líneas. `FileView`+`JsonAdapter`; JSON en `~/.config/ambxst/config/` |
| Defaults | `config/defaults/*.js` | Blueprint por dominio (bar, theme, ai, dock...) |
| Estado runtime | `modules/globals/GlobalStates.qml` | Estado transitorio NO persistente |
| Servicios | `modules/services/*.qml` | 30+ singletons: Battery, AI, Network, Clipboard... |
| Tema | `modules/theme/{Colors,Styling,Icons}.qml` | Paleta reactiva desde `~/.cache/ambxst/colors.json` |
| Primitivas | `modules/components/` | `StyledRect`, `BarPopup`, shaders GLSL |
| Panel unificado | `modules/shell/UnifiedShellPanel.qml` | `PanelWindow` full-screen para Bar+Notch+Dock |

## Convenciones obligatorias

- Singletons: `pragma Singleton` + `Singleton { id: root }`.
- Imports: namespace `qs.modules.*` (resuelto por Quickshell, sin qmldir).
- Indentación 4 espacios.
- Multi-monitor SIEMPRE con `Variants { model: Quickshell.screens }`.
- Contenedores: SOLO `StyledRect` con variantes `"pane"`, `"popup"`,
  `"common"`, `"internalbg"`, `"focus"`. Jamás `Rectangle` crudo.
- Null-safety: null-check en propiedades anidadas antes de usarlas.
- Ediciones múltiples de Config dentro de `root.pauseAutoSave`.
- Init de servicios: críticos con `Qt.callLater`, no-críticos diferidos 2s.

## Anti-patrones (bloqueantes)

- Hardcodear colores/tamaños → usa `Config.theme.*`, `Colors.*`, `Styling.*`.
- Modificar propiedades de `Config` fuera del binding `JsonAdapter`.
- Añadir propiedades a `root` en `shell.qml` → usa `GlobalStates`.
- Objetos de `JSON.parse()` en bloques `Connections` (no emiten señales QML).
- Nueva config key sin su default en `config/defaults/*.js`.

## Flujo de verificación

```bash
qs -p shell.qml    # ejecutar el shell (requiere Quickshell + Hyprland)
./cli.sh           # wrapper con control IPC
```

- No hay test suite automatizada: la verificación es visual/manual sobre Hyprland.
- Tras cambios, revisar logs de Quickshell por `TypeError: Value is undefined`
  (síntoma típico de falta de null-check o de defaults faltantes).

## Referencias de diseño

DankMaterialShell (DMS), Noctalia, end-4 dots-hyprland, MangoWC — consultar
sus repos para patrones antes de inventar estructuras nuevas.
