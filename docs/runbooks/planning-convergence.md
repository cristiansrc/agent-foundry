# Runbook — planificación que converge

Política canónica: `core/skills/spec-driven-development/SKILL.md` §10.
Introducida tras investigación documental de un workspace sin implementación
que acumuló revisiones, estados stale y re-curación tras cada transcripción.

## Uso

1. Una sesión/bloque, slice, baseline material y criterio de salida.
2. Una sección actual por estado/veredicto/carril; historia por informes enlazados.
3. Lote coherente de proyecciones mecánicas antes de revisión selectiva.
4. Hash normativo separado de metadata/índices/reportes; custodia durable.
5. Gates por fase; spike acotado aprobado cuando hace falta producir evidencia.
6. Dos rondas máximo por baseline, después informe de escape/arbitraje humano.

No es permiso para omitir findings de integridad/seguridad ni aprobar un plan
rechazado. La review selectiva sigue detectando riesgos nuevos demostrados.

## Verificación y activación

```bash
python3 -m unittest discover -s tooling/tests -p 'test_validate_states.py'
./tooling/lint.sh
python3 tooling/audit_matrix.py
./tooling/build.sh
python3 evals/run.py evals/cases/planning-convergence.yaml
```

El último comando sólo verifica formato. Certificar comportamiento requiere
la suite y `spec-validator.yaml` con `--executor opencode` sobre salidas nuevas,
además de evals de roles afectados cuando cambie su comportamiento. No instalar
un prompt sin esas evals en verde (`docs/runbooks/evals.md`). No llamar PASS de
modelo al dry-run. Instalación sólo mediante `tooling/sync.sh`, tras revisar
drift y preservar modificaciones externas; reiniciar sesión después de sync.
Después de cambios de routing del orquestador, ejecutar la suite conductual
`evals/cases/orchestrator-continuation.yaml`. Para aplicar sólo este workflow sin
pisar modelos/plugin/config ni otras skills, `tooling/sync.sh --workflow-only`
actualiza cuerpos/permisos de agentes y allowlist de skills SDLC con backup,
preserva model/variant/temperature instalados; exige evals
aplicables PASS y nunca sustituye el sync completo de otras clases de cambios.

## Migración de contextos existentes

- `Current status` primero `state: <enum>`; legacy `- planning` sigue legible.
- Un `Lane` actual; mover carriles históricos a informe.
- Un `Spec Validator Approval` actual con `invalidated_by_changes_since`.
- `not ready` histórico se conserva como rechazo en informe; dictámenes nuevos
  usan `revision-needed`. El enum lifecycle no cambia.
- El parser valida estructura y gates básicos; no certifica alcance humano,
  hashes de producto ni que una firma corresponda al snapshot por sí solo.
- Desambiguar metadata no cambia reglas/firmas por inferencia. Si falta informe
  citado, recuperar fuente o pedir review nueva acotada identificada como nueva.

## Estado de verificación del flujo (2026-10-11)

Lint/matrix/build PASS; 29 tests deterministas PASS. Los seis casos reales de
`orchestrator-continuation.yaml` pasan con Sol. El caso de Gate HPA/continuación
se repitió individualmente tras un timeout aislado45s y pasó a90s. No certifica
todos los modelos/harnesses ni todos los roles; ampliar evals sólo ante cambios
relevantes de comportamiento. Workflow-only instalado en OpenCode con backup;
bindings preservados; reiniciar el proceso.
