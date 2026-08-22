# Runbook: Cambio de Modelo o Proveedor

Procedimiento seguro para cambiar el modelo de uno o más agentes. La
arquitectura lo hace fácil; este runbook lo hace SEGURO.

## Cuándo aplica

- Un modelo se degrada/rompe (ej.: timeouts, respuestas vacías).
- Sale un modelo mejor/ más barato para un tier.
- Cambias de plan o proveedor.
- Bloqueas un modelo problemático.

## Pasos

### 1. Verificar disponibilidad del candidato

```bash
python3 tooling/test-latency.py --provider opencode          # todos
python3 tooling/test-latency.py --provider opencode --tier code_volume  # tier específico
```

Exige ONLINE antes de continuar. Si el modelo falla aquí, no avances.

### 2. Editar profiles/models.yaml

Solo este archivo. Opciones:

- **Cambiar binding de un tier**: reordena `tier_bindings.<tier>` (el primero activo gana).
- **Añadir modelo nuevo**: entrada en `models:` con `status: active` + notas.
- **Bloquear uno roto**: muévelo a la sección `blocked:` con razón y fecha.
- **Fallbacks**: ajusta cadenas si el primario puede fallar intermitentemente.

### 3. Build (regenera las 3 salidas)

```bash
./tooling/build.sh    # lint previo incluido
./tooling/status.sh   # ver qué va a cambiar en la instalación
```

### 4. Evals del agente(s) afectado(s) — NO opcional

Todo cambio de modelo debe certificarse con evals antes de instalar:

```bash
python3 evals/run.py evals/cases/spec-validator.yaml --executor opencode --model <nuevo-modelo>
python3 evals/run.py evals/cases/task-decomposer.yaml --executor opencode --model <nuevo-modelo>
python3 evals/run.py evals/cases/executor-guardrails.yaml --executor opencode --model <nuevo-modelo>
```

Si el agente cambia de comportamiento en los casos semilla → revisa si el
modelo es apto para ese rol antes de instalar. Registra el resultado en el
commit del cambio de perfil.

### 5. Instalar y verificar

```bash
echo y | ./tooling/sync.sh     # backup automático previo
./tooling/status.sh            # debe reportar SINCRONIZADO
```

Reinicia sesiones abiertas de OpenCode.

### 6. Documentar

Commit con formato:

```
chore(profiles): <qué cambió> — <razón> — <resultado de evals>
```

## Rollback

1. `git revert` del commit de profiles → build → sync.
2. O restaura backup: `tar -xzf ~/.local/share/agent-foundry/backups/<ultimo>.tar.gz -C ~/.config/opencode`.

## Checklist rápido

- [ ] Latencia OK del candidato
- [ ] Solo models.yaml editado (jamás core/)
- [ ] Build sin errores de lint
- [ ] Evals pass en agente afectado
- [ ] Sync + status sincronizado
- [ ] Commit documentando razón y resultado
