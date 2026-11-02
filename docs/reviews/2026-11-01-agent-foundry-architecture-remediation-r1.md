# Informe de remediación mecánica — ronda 1/2 (H1–H4)

**Rol:** Executor · **Fecha:** 2026-11-01 · **Baseline:** HEAD `a865eb0` (`main`), working tree con cambios preexistentes (launcher/SQLite, ítems 1-8) preservados.
**Fuente:** `docs/reviews/2026-11-01-agent-foundry-architecture-review.md` §2 (H1–H4), veredicto `changes-requested` con remediación máxima de una pasada.
**Alcance ejecutado:** solo prosa en 4 archivos autorizados. Sin tests/build/lint, sin Git mutante, sin commit.

---

## 1. Cambios aplicados

### H1 — [medio] README: eliminada la referencia falsa a `personal/`
`README.md:39-40` («Cómo funciona»):

```diff
-1. **`core/`**: agentes (`sdlc/workers|consultants|validators|guardrails`,
-   `personal/`), skills y workflow (ciclo de vida SDLC-IA con gates humanos).
+1. **`core/`**: agentes (`sdlc/workers|consultants|validators|guardrails`),
+   skills y workflow (ciclo de vida SDLC-IA con gates humanos).
```

- **Por qué no se mencionó `installer/`:** verifiqué `core/agents/installer/` (existe, 0 entradas) pero `git ls-files core/agents/installer` = **0 archivos**: un directorio vacío no se materializa en un clon, por lo que anunciarlo en el README de entrada introduciría otra afirmación no reproducible desde el VCS. Se omitió (opción conservadora permitida por H1); la estructura real queda registrada en `docs/architecture.md` C4.
- **Conteo de líneas preservado (504):** la corrección mantiene 2 líneas, de modo que la fila `master-orchestrator` sigue en `README.md:255` y la cita corregida en H3 no queda obsoleta por este mismo cambio.
- Verificado: `grep -n 'personal/' README.md` → sin ocurrencias.

### H2 — [medio] Inventario C4 completado en `docs/architecture.md` §8
`docs/architecture.md:888` (fila C4):

```diff
-| C4 | `AGENTS.md` describe `core/agents/{sdlc,personal}/`; la estructura real es `sdlc/` + `installer/` vacío, sin `personal/`. | No editado (la petición pide no tocar AGENTS salvo enlace imprescindible). Queda como deuda documental. |
+| C4 | `AGENTS.md` describe `core/agents/{sdlc,personal}/` y `README.md:39-40` repetía `personal/`; la estructura real es `sdlc/` + `installer/` vacío, sin `personal/`. | Instancia README corregida tras la remediación del dictamen `2026-11-01` (H1): solo `sdlc/workers|consultants|validators|guardrails`. `AGENTS.md` no editado (la petición pide no tocar AGENTS salvo enlace imprescindible). Queda como deuda documental. |
```

- Registra **ambas** instancias (AGENTS + README), el estado corregido de la de README y mantiene la deuda viva de `AGENTS.md` (fuera de este alcance).
- La segunda parte de H2 (caracterización del informe del executor) **no se tocó**: la instrucción prohíbe editar el reporte histórico; la corrección consta en la fila C4, exactamente como el propio dictamen admite («o dejar el informe como registro histórico y que esta corrección conste en la fila C4 y en este dictamen»).

### H3 — [bajo] ADR-0001: cita de README actualizada a la línea vigente
`docs/adr/0001-master-orchestrator-sigue-orquestando.md:9`:

```diff
-  `README.md:225`.
+  `README.md:255`.
```

- **Verificación (no número asumido):** `sed -n '255p' README.md` → fila ``| `master-orchestrator` | Consultant (consultor) | Agente Maestro y Orquestador Contextual…``.
- Queda consistente con `docs/architecture.md:138` (`[README.md:255; install-manifest.yaml:31-35]`): ambas citas del mismo lote apuntan ya a la misma línea.

### H4 — [nit] Runbook: acento restituido en el string de diagnóstico
`docs/runbooks/chatgpt-opencode-troubleshooting.md:124`:

```diff
-- `Interprete de Python no disponible` → ruta/entorno del cliente.
+- `Intérprete de Python no disponible` → ruta/entorno del cliente.
```

- **Igualdad literal con la fuente** (`tooling/opencode_mcp_launch.py:90,95,97`): comprobación programática → `literal_en_codigo=True`, `literal_en_runbook=True`. Los demás strings del runbook siguen coincidiendo con `LauncherError(...)` del launcher (comprobado en el mismo script).

---

## 2. Límites respetados

- **No editados:** `docs/reviews/2026-11-01-agent-foundry-architecture-review.md` (dictamen), `docs/reviews/2026-11-01-agent-foundry-architecture-executor.md` (registro histórico), `AGENTS.md`, `PLAN.md`, `core/**`, `profiles/**`, `adapters/**`, `tooling/**` y todo cambio preexistente del working tree.
- **Untracked preexistentes intactos:** `docs/adr/`, `docs/architecture.md`, `docs/runbooks/chatgpt-opencode-troubleshooting.md`, `docs/specs/`, `docs/reviews/` conservan su estado salvo las ediciones puntuales descritas; `tooling/opencode_mcp_launch.py` y su test no se tocaron.
- **Sin** tests, build, lint, instalación ni operaciones Git mutantes (no `add`/`commit`/`checkout`).
- Solo 4 archivos con mtime de esta pasada (verificado con `find -newermt`): `README.md`, `docs/architecture.md`, `docs/adr/0001-…md`, `docs/runbooks/chatgpt-opencode-troubleshooting.md`.

---

## 3. Evidencia de verificación

| Verificación | Comando | Resultado |
|---|---|---|
| Integridad de baseline | `git rev-parse --short HEAD` | `a865eb0` |
| Estado del árbol | `git status --porcelain` | mismos `M`/`??` preexistentes; sin archivos nuevos por esta pasada |
| Diff de README | `git diff -U2 -- README.md` | un solo hunk nuevo en 39-40; resto = cambios preexistentes del lote |
| Whitespace/conflictos | `git diff --check` | **exit 0** |
| Cita ADR | `sed -n '255p' README.md` + `grep -n 'README.md:255'` | fila `master-orchestrator`; ADR:9 y architecture:138 coinciden |
| Enlaces relativos | script sobre README, architecture, ADR-0001/0002/índice y runbook | **25 comprobados, 0 roto** |
| Secreto — delta por archivo | `gitleaks dir <archivo> --redact` (v8.30.1) | **0 hallazgos en los 6 archivos del delta** |
| Secreto — diff Git | `gitleaks git --pre-commit --verbose --redact` | `no leaks found` (exit 0) |
| Secreto — árbol completo (control) | `gitleaks dir . --redact` + reporte JSON | 2 hallazgos **preexistentes y fuera del delta**, rutas: `.opencode/foundry-install.json:6` y `tooling/tests/test_opencode_mcp_launch.py:17` (recibo local gitignored y fixture de credencial falsa ya clasificados en el dictamen §3). Valores **no** reproducidos. |

**Nota sobre el scan de directorio inicial:** `gitleaks dir README.md docs/...` reportó 2 leaks y 4.4 MB escaneados; el aislamiento por archivo demuestra que **ninguno pertenece al delta** (los 6 archivos dan 0). El árbol completo confirma que son los dos preexistentes citados.

---

## 4. Riesgo residual

1. **Re-review:** pendiente **una** re-review selectiva (no global) sobre los puntos editados: README:39-40, C4 de `architecture.md` §8, ADR-0001:9, runbook:124. El resto del lote ya está verificado en el dictamen §3.
2. **H5 (fuera del lote):** `adapters/chatgpt/skills/opencode-control/SKILL.md:7` sigue nombrando `get_session_statuses` (plural) frente a `get_session_status` del código. Deuda para un carril trivial futuro.
3. **Deudas declaradas sin cambio:** C3 (`docs/runbooks/mcps.md` con bindings retirados), C8 (conteo de skills desktop en runbook) y la instancia `AGENTS.md:39` de C4.
4. **Hallazgos de secretos preexistentes:** fuera del delta y ya evaluados; requieren decisión de su owner (fixture/recibo local), no de esta remediación. El delta está limpio.

## 5. Siguiente acción

Handoff al orquestador para persistencia literal de este informe por Documentation y para solicitar la **re-review selectiva de ronda 1** sobre los 4 puntos citados + gitleaks del delta. No procede build/lint/tests ni Git mutante en este carril.