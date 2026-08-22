---
name: ambxst-plugins
description: Cómo extender ambxst con nuevas features/plugin-modules end-to-end (clave de config, servicio, UI, integración en notch/bar/dashboard) siguiendo el patrón de módulos existentes.
---

# Skill: ambxst Plugin & Feature Development

Protocolo para añadir una feature completa al shell ambxst. Un "plugin" en
ambxst = nuevo módulo con (1) claves de configuración, (2) servicio singleton
si toca el sistema, (3) componente UI, (4) punto de integración
(bar/notch/dashboard/launcher).

## Receta end-to-end (orden estricto)

### 1. Claves de configuración (SIEMPRE primero)
- Añade defaults en `config/defaults/<dominio>.js` (o dominio nuevo).
- Expón las propiedades en `config/Config.qml` con su par `FileView`/`JsonAdapter`.
- Restricciones de valor van en `ConfigValidator.js` (ej. enums permitidos).
- Sin default en defaults/*.js la feature está PROHIBIDA (rompe bootstrap).

### 2. Servicio (si hay I/O o estado de sistema)
- Crea `modules/services/MiFeatureService.qml` como singleton:
  `pragma Singleton` + `Singleton { id: root }`.
- Procesos externos con `Process` + `StdioCollector`; parseo defensivo.
- Estado transitorio compartido va en `GlobalStates.qml`, nunca en root global.
- Persistencia de sesión: usa el patrón de `StateService.qml` (JSON en disco).

### 3. Componente UI
- Contenedores con `StyledRect` (variantes: pane/popup/common/internalbg/focus).
- Colores vía `Colors.*` / tamaños vía `Styling.radius()`/`fontSize()`.
- Bindings contra `Config.<dominio>.<prop>`; nada de estado local para settings.
- Si va en el panel unificado, respeta la estructura de `UnifiedShellPanel.qml`.

### 4. Integración
- **Notch**: nueva pestaña en `modules/widgets/dashboard/` (usa lazy-loading LRU
  del dashboard si es pesado) o vista en `defaultview/` si es compacta.
- **Bar**: widget en `modules/bar/` registrado en `BarContent.qml` (grupos de
  widgets, auto-hide, orientación horizontal/vertical).
- **Launcher**: entrada en `LauncherView.qml` si es una acción buscable.
- Toggle rápido: tarjeta en dashboard con switch ligado a Config.

### 5. Verificación manual
```bash
qs -p shell.qml   # probar en vivo; borrar ~/.cache/ambxst si hace falta reset
```
- Verifica: carga inicial (sin undefined), guardado de config tras reload,
  comportamiento multi-monitor, y que el JSON en `~/.config/ambxst/config/`
  contiene las claves nuevas con valores por defecto correctos.

## Checklist final

- [ ] defaults/*.js actualizado + validador si aplica
- [ ] Singleton service con init diferido apropiado (crítico vs no-crítico)
- [ ] UI solo con StyledRect + tema reactivo (cero hardcodeo)
- [ ] Integración registrada en su punto (bar/notch/dashboard)
- [ ] Probado en vivo con reload de Quickshell
