# Informe de re-review selectiva — ronda 1/2 (H1–H4)

**Rol:** Reviewer · **Fecha:** 2026-11-01 · **Baseline:** HEAD `a865eb0` (`main`) — intacto.
**Fuente:** `docs/reviews/2026-11-01-agent-foundry-architecture-remediation-r1.md` (remediación mecánica H1–H4) sobre dictamen `docs/reviews/2026-11-01-agent-foundry-architecture-review.md` §2 (veredicto `changes-requested`, remediación máxima una pasada).
**Alcance:** solo los 4 puntos editados + límites de la pasada + gitleaks del delta. Sin re-review global (el resto del lote ya está verificado en el dictamen §3), sin edición de archivos, sin build/tests/lint, sin Git mutante (solo lectura).

---

## 1. Hallazgos

**Ninguno.** Los 4 hallazgos H1–H4 están corregidos exactamente como el dictamen exigía, sin cambios fuera de los targets autorizados y sin daño a cambios preexistentes. Detalle y evidencia por punto:

### H1 — README sin `personal/` ✅
- `README.md:39-40` lee ahora `agentes (sdlc/workers|consultants|validators|guardrails)` — la variante «dejar solo sdlc/…» que el dictamen autorizaba expresamente (línea 25).
- `grep -n 'personal/' README.md` → **0 ocurrencias** (exit 1).
- `git diff -U2 -- README.md` → un único hunk nuevo (`@@ -36,6 +37,6 @@`) eliminando `personal/`; conserva 2 líneas, `wc -l README.md` = **504** como declara la remediación, por lo que la cita de H3 no queda desplazada.
- La omisión de `installer/` (vacío, 0 archivos en `git ls-files`) es la opción conservadora permitida; la estructura real queda registrada en la fila C4.

### H2 — Fila C4 completa con ambas instancias y estado corregido ✅
- `docs/architecture.md:888` (verificado con `grep -n '^| C4'`) registra **ambas** instancias: `AGENTS.md` **y** `README.md:39-40` («repetía `personal/`»), con estado «Instancia README corregida tras la remediación del dictamen `2026-11-01` (H1)» y la deuda `AGENTS.md` viva.
- El informe executor (`:48`) **no fue editado** (mtime `23:08:26`, anterior a la pasada) — opción «dejar el informe como registro histórico» que el propio dictamen admitía (línea 31); la disposición consta en la fila C4, en el informe de remediación y en este dictamen de re-review.

### H3 — ADR-0001 cita la línea vigente ✅
- `docs/adr/0001-master-orchestrator-sigue-orquestando.md:9` = `README.md:255`.
- `sed -n '255p' README.md` → fila ``| `master-orchestrator` | Consultant (consultor) | Agente Maestro y Orquestador Contextual…`` (número verificado, no asumido).
- Consistente con `docs/architecture.md:138` (`[README.md:255; …]`): ambas citas del lote apuntan a la misma línea. Las menciones residuales de `README.md:225` existen solo en el dictamen original (registro histórico inmutable, correcto), en el diff citado por el informe de remediación y en el tracker `docs/specs/.working/…sdd-context.md:71`, que describe el hallazgo *como se encontró* con estado `addressed-pending-review` — ninguno es cita normativa vigente.

### H4 — String literal idéntico a la fuente ✅
- `docs/runbooks/chatgpt-opencode-troubleshooting.md:124` = `Intérprete de Python no disponible` (acento restituido).
- Igualdad **byte-exacta** con `tooling/opencode_mcp_launch.py` (comprobación `grep -cF`): «Intérprete de Python no disponible» → 1 en runbook / 3 en launcher (líneas 90, 95, 97); «servidor MCP no disponible» → 1/1; «raíz de proyectos inválida» → 1/2; «No se pudo obtener la credencial» → 1/3. Todos los strings citados coinciden literalmente con `LauncherError(...)`.

## 2. Límites de la pasada — sin cambios fuera de los targets

- **Ventana de escritura exacta (23:24:50–23:24:55):** `find` sobre el árbol (excl. `.git`) → exactamente los 4 archivos: `README.md`, `docs/architecture.md`, `docs/adr/0001-…md`, `docs/runbooks/chatgpt-opencode-troubleshooting.md`. Nada más.
- **Línea de tiempo coherente:** dictamen original 23:22:11 (escrito *antes* del burst, no editado por la remediación); executor 23:08:26; PLAN.md 23:01:28; ADR-0002/índice 23:01:14; tooling 16:48/10-31 — todos anteriores e intactos. Informe r1 23:45:27 y tracker sdd-context 23:46:26 son post-pasada (persistencia/spot-check de Documentation), no parte del delta.
- **`git status --porcelain`:** mismo conjunto preexistente (8 `M` + 7 `??`); sin archivos nuevos por esta pasada; `AGENTS.md` no modificado; `HEAD` = `a865eb0`.
- **Cambios preexistentes ilesos:** hunks del lote intactos en el diff de README (+1 índice, `#skills-75`, anchors ChatGPT/Kiro, +21 «Arquitectura y roadmap», «23 suites», +8 párrafo MCP, corrección C2 en 227–230); launcher/SQLite (ítems 1-8) sin tocar.

## 3. Bloque generado de README

- Marcadores `<!-- BEGIN:GENERATED-TABLES -->` (línea 236) / `<!-- END:GENERATED-TABLES -->` (línea 504): ningún hunk del diff (vs HEAD) alcanza la región ≥236; H1 (39-40) cae fuera del bloque.
- **Comparación literal bloque generado working-tree vs `HEAD:README.md`:** extracción con `sed` de ambos y `diff` → **IDÉNTICO** (269/269 líneas). El bloque no fue dañado ni manualmente alterado; la fila `master-orchestrator` citada por H3 (línea 255) vive dentro de un bloque intacto.

## 4. Gitleaks — solo delta revisado

`gitleaks dir <archivo> --redact` (v8.30.1) sobre los 4 archivos del delta → **`no leaks found`** en los 4 (README ~35.78 KB, architecture ~57.49 KB, ADR-0001 ~2.44 KB, runbook ~16 KB). Sin scan de árbol completo (los 2 hallazgos preexistentes fuera del delta —`.opencode/foundry-install.json`, fixture de test— ya están clasificados en el dictamen §3 y requieren decisión de su owner, no de esta re-review).

## 5. Riesgo residual (sin cambio respecto al dictamen)

H5 (`adapters/chatgpt/skills/opencode-control/SKILL.md:7`, `get_session_statuses` vs `get_session_status`), C3 (`mcps.md`), C8 y la instancia `AGENTS.md` de C4 siguen inventariados como deuda declarada, fuera de este delta. Launcher/SQLite permanece «implementado local, pendiente de integración/revisión» — corresponde a otro incremento. Nada de esto bloquea este carril.

## 6. Veredicto

Revisión selectiva de ronda 1 sobre los 4 puntos editados + límites + gitleaks del delta: **todos los hallazgos H1–H4 remediados correctamente, sin hallazgos nuevos, sin daño colateral**. No se requiere ronda 2 de remediación. Handoff al orquestador: persistencia literal de este informe por Documentation y actualización de estado del tracker (H1–H4: addressed → remediated/approved ronda 1).

`review: approved`

`security_surface: no`