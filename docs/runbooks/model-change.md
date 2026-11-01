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
- **Forzar un modelo para un agente sin crear un tier**: `slot:` en `agent_tiers`
  (el tier queda como respaldo si el slot falla; solo lo honra el adapter OpenCode).
- **Añadir modelo nuevo**: entrada en `models:` con `status: active` + notas.
- **Bloquear uno roto**: muévelo a la sección `blocked:` con razón y fecha.
- **Fallbacks**: ajusta cadenas si el primario puede fallar intermitentemente.

### 3. Build (regenera las 3 salidas)

```bash
./tooling/build.sh    # lint previo incluido
./tooling/status.sh --project <ruta>   # ver qué cambiaría en el proyecto
```

### 4. Evals del agente(s) afectado(s) — NO opcional

Todo cambio de modelo debe certificarse con evals antes de instalar:

```bash
python3 evals/run.py evals/cases/spec-validator.yaml --executor opencode --model <nuevo-modelo>
python3 evals/run.py evals/cases/task-decomposer.yaml --executor opencode --model <nuevo-modelo>
python3 evals/run.py evals/cases/executor-guardrails.yaml --executor opencode --model <nuevo-modelo>
```

Flags útiles: `--repeat N` (los LLM no son deterministas; exige mayoría o
`--threshold`), `--timeout` (default 900s; modelos de razonamiento pesado
pueden necesitar más), `--show-output` (diagnóstico de fallos). Cada caso
corre en un sandbox temporal (`opencode run --dir`), nunca en este repo.
Detalle en [`docs/runbooks/evals.md`](evals.md).

Si el agente cambia de comportamiento en los casos semilla → revisa si el
modelo es apto para ese rol antes de instalar. Registra el resultado en el
commit del cambio de perfil.

### 5. Instalar y verificar

```bash
./tooling/sync.sh --project <ruta> --apply   # backup automático previo
./tooling/status.sh --project <ruta>         # debe reportar 0 diferencias
```

Reinicia sesiones abiertas de OpenCode.

La instalación siempre aplica un bundle completo y versionado. Si hay
prompts o permisos pendientes de certificación, no instalar hasta evaluarlos.

### 6. Documentar

Commit con formato:

```
chore(profiles): <qué cambió> — <razón> — <resultado de evals>
```

## Rollback

1. `git revert` del commit de profiles → build → sync.
2. O restaura los archivos desde `<proyecto>/.opencode/backups/<fecha>/`.

## Checklist rápido

- [ ] Latencia OK del candidato
- [ ] Solo models.yaml editado (jamás core/)
- [ ] Build sin errores de lint
- [ ] Evals pass en agente afectado
- [ ] Sync + status sincronizado
- [ ] Commit documentando razón y resultado
