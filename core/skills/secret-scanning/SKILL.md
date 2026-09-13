---
name: secret-scanning
description: Escaneo obligatorio de secretos con Gitleaks para agentes que escriben, validan o versionan artefactos del repositorio.
---

# Secret Scanning con Gitleaks

Protege el repositorio contra API keys, tokens, contrasenas, credenciales cloud,
claves privadas y otros secretos accidentales. Aplica solo dentro del
repositorio activo.

## Cuando usarlo

- Despues de crear o modificar archivos.
- Antes de entregar un handoff de archivos escritos.
- Antes de hacer `git add` o un commit.
- Durante la validacion final de un incremento.

## Comandos obligatorios

Para cambios del working tree, incluyendo modificaciones no staged:

```bash
gitleaks git --pre-commit --verbose
```

Para confirmar el contenido que entrara en el commit:

```bash
gitleaks git --staged --verbose
```

Para auditar todo el historial cuando el alcance lo requiera:

```bash
gitleaks git --verbose
```

## Reglas de bloqueo

- Si `gitleaks` no esta instalado, detenerse con `Blocked: gitleaks unavailable`.
- Si detecta un secreto, detenerse con `Blocked: secret detected`.
- No incluir el valor secreto en la respuesta, logs, shared context o reporte.
- No usar allowlists, `gitleaks:allow` ni baselines para ocultar un hallazgo sin
  una decision explicita del responsable de seguridad.
- Un secreto detectado debe eliminarse del cambio y revocarse o rotarse si pudo
  estar expuesto. Borrarlo solo del archivo actual no limpia el historial.

## Documentacion segura

Usar placeholders en ejemplos y configuraciones:

```text
API_KEY=<replace-with-secret>
Authorization: Bearer ${ACCESS_TOKEN}
```

Nunca copiar tokens reales a README, specs, fixtures, logs, capturas o
shared contexts.

## Evidencia de handoff

Registrar solo el comando y el resultado, sin salida cruda ni valores
detectados:

```text
secret_scan: gitleaks git --pre-commit --verbose -> pass
```
