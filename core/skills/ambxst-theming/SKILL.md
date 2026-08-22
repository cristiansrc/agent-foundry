---
name: ambxst-theming
description: Sistema de theming de ambxst — generación de paleta con matugen desde wallpaper, colores reactivos del shell y sincronización en vivo con GTK (adw-gtk3), Qt/KDE (kdeglobals + D-Bus) y Kitty.
---

# Skill: ambxst Theming & Color Sync

Cómo funciona el sistema de temas de ambxst y cómo extender la sincronización
de colores a otras aplicaciones.

## Pipeline de color

```
wallpaper → matugen → ~/.cache/ambxst/colors.json → Colors.qml (reactivo)
                                                   ├→ GTK 3/4 (adw-gtk3 variantes)
                                                   ├→ Qt/KDE (kdeglobals + .colors + D-Bus)
                                                   └→ Kitty (fuentes/colores exportados)
```

- `modules/theme/Colors.qml` observa `~/.cache/ambxst/colors.json` con
  `FileView`: cualquier escritura al JSON repinta el shell EN VIVO.
- Presets manuales en `assets/presets/` y generación automática matugen
  configurada bajo `assets/matugen/`.

## Reglas para el shell

- NUNCA hardcodear hex en QML: siempre `Colors.*` / `Config.theme.*`.
- Componentes nuevos deben verse correctos con presets claro Y oscuro.
- Si una feature necesita un rol de color nuevo, añádelo al pipeline
  (matugen template o preset) antes de usarlo.

## Sincronización con apps externas

### GTK 3/4 (Nautilus, Thunar)
- Variantes adw-gtk3 / adw-gtk3-dark según esquema prefer-light/prefer-dark.
- El sync debe aplicar tema Y preferencia de esquema; probar ambas direcciones.

### Qt / KDE (Dolphin)
- Generar `kdeglobals` + archivo `.colors` del esquema activo.
- Tras escribir el scheme, emitir señal D-Bus para recarga instantánea de apps
  Qt vivas (sin ella, los cambios requieren reiniciar cada app).

### Terminal (Kitty)
- Exportar config de fuentes del shell a las instancias Kitty dinámicamente.

## Al añadir un target nuevo de sincronización

1. Localiza el formato nativo del objetivo (template matugen si aplica).
2. Escribe el generador junto a los existentes (mismo estilo de scripts).
3. Dispara por el mismo evento que los demás targets (cambio de wallpaper,
   preset, toggle light/dark) — un solo punto de verdad temporal.
4. Verifica EN CALIENTE: cambia wallpaper y confirma repaint sin reiniciar apps.

## Checklist

- [ ] Funciona con presets claro/oscuro y con matugen (wallpapers claros y oscuros)
- [ ] Recarga en vivo sin restart del shell ni de las apps objetivo
- [ ] Multi-monitor no rompe el esquema (mismo tema en todas las salidas)
- [ ] Ningún valor de color quedó hardcodeado fuera de templates
