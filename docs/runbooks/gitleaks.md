# Gitleaks — protección contra secretos

`gitleaks` analiza el repositorio y los cambios staged para detectar secretos
que no deben entrar en Git: API keys, tokens, contraseñas, credenciales cloud y
claves privadas.

## Instalación en Arch Linux

```bash
sudo pacman -S --needed gitleaks
gitleaks version
```

El paquete oficial se publica en el repositorio `extra`. En otra distribución,
instala la versión oficial desde <https://github.com/gitleaks/gitleaks/releases>
y confirma que el binario `gitleaks` esté disponible en `PATH`.

## Uso manual

Escanear únicamente lo staged antes de un commit:

```bash
gitleaks git --staged --verbose
```

Escanear el historial completo del repositorio:

```bash
gitleaks detect --source . --verbose
```

Un hallazgo debe eliminarse del cambio y, si el secreto pudo estar expuesto,
revocarse o rotarse. No basta con borrar el valor del archivo actual si sigue
presente en el historial.

## Hook del repositorio

La plantilla versionada está en `tooling/hooks/pre-commit`. Instálala en el
repositorio activo con:

```bash
cp tooling/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

El hook ejecuta primero `gitleaks git --staged --verbose`, después el lint y
la auditoría de la matriz. Si `gitleaks` no está instalado o detecta un
secreto, el commit se detiene.
