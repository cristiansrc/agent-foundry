---
name: ambxst-packaging
description: Empaquetado e instalación de ambxst — install.sh multi-distro (Arch/Fedora/NixOS), flake.nix, dependencias Quickshell/Hyprland y flujo de release del fork personal.
---

# Skill: ambxst Packaging & Install

Cómo empaquetar, instalar y distribuir el fork personal de ambxst.

## Vías de instalación

| Vía | Archivo | Destino típico |
|-----|---------|----------------|
| Script interactivo | `install.sh` | Instalación en $HOME + deps por distro |
| Nix | `flake.nix` + `nix/` | Reproducible (NixOS / home-manager) |
| Wrapper runtime | `cli.sh` | Lanzador con control IPC (`qs -p shell.qml`) |

## install.sh

- Detecta distro (Arch/Fedora/NixOS) e instala dependencias: quickshell,
  hyprland/hyprland-qtutils, matugen, pam para lockscreen, fuentes Phosphor,
  servicios opcionales (network, bluetooth, easyeffects).
- Copia assets a sus rutas (~/.config/ambxst, ~/.cache/ambxst se crea al vuelo).
- Regla del fork: mantener compatibilidad upstream Axenide/Ambxst donde sea
  posible; features propias documentadas en README (sección Key Custom Features).

## flake.nix

- Estructura en `nix/`: packages + module definitions.
- Al añadir dependencia nueva: actualizar AMBOS `flake.nix` y `install.sh`
  (mismo criterio que config/defaults: dos fuentes de instalación deben quedar
  consistentes).
- `flake.lock` se commitea siempre; renovar conscientemente, no por rutina.

## Checklist de release del fork

1. Versión bump en archivo `version`.
2. Probar instalación limpia en VM o entorno desechable si el cambio toca deps.
3. Verificar arranque: `qs -p shell.qml` sin errores en log.
4. Ejecutar la variante Quickshell/QML del bucle `verify-code.sh`
   (qmllint + shellcheck + qmltestrunner/bats; definida en
   `code-quality-and-sonarqube` §4) si el cambio toca QML o scripts.
5. Commit semántico + push a `cristiansrc/ambxst`.
6. Si el cambio es relevante como changelog upstream, proponerlo aparte (no
   mezclar changelog propio con el del proyecto original).

## Riesgos conocidos

- axctl (binario Go en /usr/local/bin) NO se reinstala vía install.sh estándar:
  build+replace manual (`go build -o bin/axctl .`); el daemon corre en la sesión
  del usuario y no puede validarse desde el agente.
- Cambios en PAM (lockscreen) pueden bloquear el login: probar SIEMPRE lockscreen
  en una sesión desechable antes de cerrar el cambio.
