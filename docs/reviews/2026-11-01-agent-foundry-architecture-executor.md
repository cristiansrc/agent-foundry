## Informe de implementación documental

### Baseline
- HEAD: a865eb0 (main), working tree con cambios preexistentes.
- Estado inicial preservado: `.gitignore`, `docs/runbooks/chatgpt-opencode-phase2.md`, `tooling/opencode_bridge.py`, `tooling/opencode_mcp.py`, `tooling/tests/test_opencode_bridge.py`, `tooling/tests/test_opencode_mcp.py`, `tooling/opencode_mcp_launch.py` y `tooling/tests/test_opencode_mcp_launch.py` quedaron intactos.
- No se ejecutó build, lint, tests ni Git mutante. No hay commit.
- Odd-card: sin cambios.

### Paths creados
| Path | Contenido |
|---|---|
| `docs/architecture.md` | Arquitectura canónica: as-built, reconstrucción de fases 1/1.5/2/2.1/2.2, MCP local, control plane propuesto, ciclo de mejora y roadmap 3+. |
| `docs/adr/README.md` | Índice y convención de ADRs. |
| `docs/adr/0001-master-orchestrator-sigue-orquestando.md` | Decisión registrada: Desktop observa, `master-orchestrator` orquesta. |
| `docs/adr/0002-mcp-local-lectura-sin-escritura.md` | Decisión registrada: MCP stdio read-only, alcance por proyecto, secreto vía Secret Service. |
| `docs/runbooks/chatgpt-opencode-troubleshooting.md` | Runbook operativo de MCP/Desktop, D-Bus, auth y ventana de sesiones 1.18.31. |

### Paths modificados
| Path | Cambio |
|---|---|
| `README.md` | Prosa fuera de `BEGIN/END:GENERATED-TABLES`: nueva sección “Arquitectura y roadmap”, párrafo del MCP local, corrección de visión (GPT-6 Luna/MiMo/GLM), 23 suites y anclas del índice. Bloque generado verificado idéntico a HEAD. |
| `PLAN.md` | Resumen de integración por fases, enlace a arquitectura y nota de vigencia C5/C6. No se reabrieron decisiones. |

### Evidencia y verificaciones
- Fuentes inspeccionadas: `AGENTS.md`, `README.md`, `PLAN.md`, `install-manifest.yaml`, `docs/runbooks/*` (fases 1/1.5/2, desktop-skills, mcps, harness, agent-operations, model-router, evals, model-change), `docs/investigations/*`, `tooling/opencode_bridge.py`, `tooling/opencode_mcp.py`, `tooling/opencode_mcp_launch.py`, tests MCP, `profiles/*.yaml`, `core/workflow/states.md`, plugins observer/guardian, skills desktop y estado/diff Git.
- Conteos reproducibles: 27 agentes en `core/agents/`, 75 `SKILL.md`, 23 suites en `evals/cases/`, 23 agentes renderizados en `adapters/opencode/out/agents/`.
- Fase 1.5: citada como evidencia histórica (48 tests, lint, matriz 0, build, API 1.18.31, sesión/eventos, simulación). No re-ejecutada.
- Codex CLI/ChatGPT Desktop: no se inventaron resultados. El documento declara que no hay evidencia de llamada exitosa; cita los fallos registrados (copia de skills por `Read-only file system`, CLI 2.1.2 incompatible, `ProviderModelNotFoundError`, ausencia de conexión directa verificada) y marca el resto como aportado/no reproducible.
- Enlaces: chequeo relativo de los documentos nuevos/modificados → `LINKS OK`.
- Secret scan: `gitleaks dir docs --redact --no-banner` → exit 0, no leaks; `gitleaks dir README.md`, `PLAN.md`, `docs/adr` y runbook → exit 0; `gitleaks git --pre-commit --verbose` → exit 0.
- Diff: `git diff --check` → exit 0. Sin trailing whitespace real; los avisos iniciales eran falsos positivos del patrón.
- README generado: comparación literal contra `HEAD:README.md` → `IDENTICAL`.

### Contenido cubierto
- Reconstrucción de fases con estados implementado y verificado / implementado pendiente / propuesto / histórico, separando evidencia aportada por el usuario de la reproducible.
- Las 5 herramientas MCP, launcher Secret Service, D-Bus, autenticaciones separadas (OpenCode Go, ChatGPT/OpenAI, API HTTP local, Secret Service, MCPs de agentes), aislamiento por proyecto, fallback SQLite, `source=local`, `complete=false`.
- Límites explícitos: sin observabilidad en vivo, sin ejecución remota, sin escritura, sin respuesta de permisos, sin acreditación de Desktop.
- Control plane futuro con Observability Collector, Execution Auditor, Flow Analyzer, Permission Guardian en simulación, Evolution Engine y knowledge management; inputs/outputs/ownership/trust/privacy/métricas/restricciones Alfa/riesgos/aceptación.
- Ciclo baseline → pruebas → HPA/validación humana → piloto → rollback.
- Roadmap 3+ con dependencias, métricas y criterios medibles.
- Contradicciones C1–C12 con autoridad citada; solo se corrigió prosa bajo alcance (README/PLAN). `AGENTS.md` y `mcps.md` no se tocaron.

### Límites
- No se ejecutaron tests, lint, build ni evals; era una tarea documental y la petición prohibía build.
- No se verificó una conexión real desde ChatGPT Desktop/Codex CLI ni se inspeccionó el `.db` real.
- La etiqueta “Fase 2.1” se reconstruye por el orden del runbook y el diff local; el runbook no la rotula. Queda advertido en el documento.
- Limitación documentada: el launcher no reenvía `--opencode-db`; con launcher, el respaldo SQLite solo autodetecta la ruta por defecto.
- Deuda documental pendiente fuera de alcance: C3 (`mcps.md`), C4 (`AGENTS.md`) y C8 (conteo de skills desktop).
- Los cambios locales de launcher/SQLite siguen siendo “implementados localmente, pendientes de integración/revisión”; requieren revisión e integración por el rol autorizado.
