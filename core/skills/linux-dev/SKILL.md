---
name: linux-dev
description: Estándares de programación sobre Linux — bash estricto, servicios systemd, D-Bus, jerarquía de archivos, permisos y empaquetado básico. Para scripts, daemons de usuario e integraciones de escritorio Wayland/X11.
---

# Skill: Linux Development Standards

Estándares para programar sobre GNU/Linux: scripts de sistema, servicios,
integración de escritorio y automatización.

## Bash estricto

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

- `-e`: abortar en error · `-u`: variables no definidas fallan · `-o pipefail`
  propagar fallos de pipes.
- Siempre `readonly` para constantes; variables locales en funciones con `local`.
- Comillas dobles en TODA expansión `"$var"`; nunca parsear `ls`; usar arrays.
- Dependencias externas: verificar con `command -v jq >/dev/null || exit 1`.
- Temporales con `mktemp`; limpieza con `trap cleanup EXIT`.
- Scripts largos: logging a stderr (`echo "..." >&2`) y `--dry-run` cuando
  el script muta estado.

## systemd

- Unidades de USUARIO preferidas (`~/.config/systemd/user/*.unit`) para todo
  lo que no requiera root; habilitar con `systemctl --user enable --now X`.
- Servicios que escriben logs: `journalctl --user -u X -f` es la fuente única;
  no escribir logs propios paralelos.
- `Type=notify` > `Type=forking`; siempre `Restart=on-failure` con
  `RestartSec=` razonable; declarar `After=`/`Requires=` reales, no decorativos.
- Timers > cron en desktop moderno (`OnCalendar`, `Persistent=true`).
- Hardening mínimo para unidades de sistema: `NoNewPrivileges=yes`,
  `ProtectSystem=strict`, `PrivateTmp=yes`.

## D-Bus

- Descubrir antes de programar: `busctl --user tree`, `gdbus introspect`.
- Desde QML/scripts usar las interfaces documentadas del compositor/servicio;
  emitir señales en lugar de polling para notificar cambios de estado.
- Sesión vs sistema: apps de escritorio casi siempre usan el bus de sesión
  (`--user`). Nunca hardcodear direcciones de bus.

## Jerarquía y permisos

- Config de usuario: `$XDG_CONFIG_HOME` (~/.config); datos: `~/.local/share`;
  cache descartable: `~/.cache` — jamás escribir configs fuera de XDG dirs.
- Ejecutables locales de usuario: `~/.local/bin`; de sistema: `/usr/local/bin`
  (nunca tocar `/usr/bin`, lo gestiona el package manager).
- Scripts instalados: 0755, owner root solo si es de sistema; secrets JAMÁS en
  el repo ni con perms world-readable (`chmod 600`).

## Escritorio Wayland (Hyprland y afines)

- Consultas: `hyprctl monitors -j | jq`, protocolos wlr via herramientas del
  compositor; no parsear salida humana, siempre flags `-j` + jq.
- Capturas/clipboard vía protocols estándar (grim/slurp/wl-copy), verificando
  disponibilidad del protocolo antes de invocar.
- Multi-monitor: iterar salidas reales, asumir nada sobre nombres (DP-1, eDP-1).

## Verificación mínima antes de entregar

1. `shellcheck script.sh` sin warnings de severidad alta.
2. Ejecutar una vez real + una vez con condición de error forzada.
3. Si instala archivos: listar qué dejó instalado y cómo desinstalarlo.
