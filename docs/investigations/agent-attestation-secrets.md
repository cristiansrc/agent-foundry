# Investigación: prueba de ejecución por agentes + secreto de sus definiciones

Fecha: 2026-09-30. Estado: **investigación** (sin implementar).
Complementa `github-codespaces-sdlc.md`. Dos problemas:

- **A. Prueba**: saber con certeza que un trabajo lo ejecutaron NUESTROS
  agentes (no a mano ni con otros medios) y rechazarlo si no. Validación
  determinista, sin LLM.
- **B. Secreto**: que los proveedores puedan USAR los agentes sin VER sus
  definiciones (prompts), hoy y con futura info alfa.

## 1. Conclusión anticipada

Ambos se resuelven con la misma arquitectura: **un wrapper de confianza
(`foundry-attest`) + recibos firmados + prompts cifrados**. El proveedor
puede usar cualquier IDE, pero sin un recibo válido su PR no mergea, y sin
la llave no puede leer ni ejecutar los prompts por su cuenta.

Límite honesto: se prueba el **proceso** (qué agente, con qué prompt
exacto, sobre qué inputs, produciendo qué outputs), no la autoría
keystroke-por-keystroke. Proceso probado + reviewer + tests + gates humanos
es la garantía completa; nada más es posible sin ejecución bloqueada.

## 2. Hallazgos (verificados 2026-09-30)

### 2.1 Artifact Attestations (`actions/attest@v4`)

- Firma Sigstore **sin llaves** (certificado efímero vía OIDC del workflow:
  permisos `id-token: write`, `attestations: write`).
- Tres modos: provenance (SLSA), SBOM y **custom predicate** (in-toto con
  predicado propio) — el modo custom es el que sirve para recibos de agente.
- Verificación con `gh attestation verify` (también offline); el bundle
  queda asociado al repo, workflow, commit y run que lo produjo.
- En repos privados requiere Enterprise Cloud (el plan que la empresa va a
  adquirir). En públicos vale cualquier plan.
- La doc recomienda NO firmar archivos sueltos de código: se firma un
  **manifiesto/recibo** con los hashes, no cada fuente.
- Fuente: docs de GitHub (artifact attestations), repo actions/attest.

### 2.2 sops + age para prompts cifrados en el repo

- `sops` cifra YAML/JSON/ENV/BINARIO con `age` (recomendado sobre PGP);
  el descifrado en CI es una env var (`SOPS_AGE_KEY`) — encaja con
  environment secrets gating por aprobación.
- Los prompts `.md` se cifran como binario o se convierten a un formato
  soportado; el wrapper descifra a un tmpfs solo en memoria del job.
- Fuente: getsops/sops, gist de referencia, docs de secrets en Actions.

### 2.3 Permisos de lectura en GitHub son por repo, no por ruta

No existe "este team no puede leer `docs/alfa/`" dentro de un repo.
Todo lo sensible vive en **repos privados separados**; el repo de trabajo
solo recibe packs redactados. CODEOWNERS y rulesets controlan escritura y
aprobación, jamás lectura.

### 2.4 Un Codespace es del desarrollador

Todo lo que hay en su filesystem lo puede leer (es su usuario). Conclusión:
**ningún secreto sobrevive dentro del Codespace de un proveedor**. Los
prompts o van cifrados (sin llave para él) o la ejecución ocurre fuera
(runner corporativo) y él solo ve el resultado.

## 3. Diseño A: recibos firmados de ejecución

### 3.1 Formato del recibo (JSON, compatible in-toto)

```json
{
  "agent": "executor",
  "lane": "feature",
  "increment": "012-pagos",
  "prompt_bundle": "sha256:<hash de core/ usado>",
  "model": "opencode-go/deepseek-v4.1-flash",
  "inputs": {"spec": "sha256:..", "task_board": "sha256:.."},
  "outputs": [{"path": "src/...", "sha256": ".."}],
  "nonce": "<emitido por el Action de aprobación>",
  "session": "ses_..", "at": "2026-..", "base_sha": "..", "head_sha": ".."
}
```

- El `nonce` lo emite el Action al aprobar la tarea y debe venir en el
  recibo: ata el recibo a una tarea autorizada e impide **replay** de
  recibos viejos.
- `prompt_bundle` ata el recibo a la versión exacta de prompts: si alguien
  modifica un prompt por su cuenta, el hash no coincide con el esperado.

### 3.2 Emisor: wrapper `foundry-attest` (único firmante)

```
provider ejecuta: foundry-attest --agent executor --nonce <..> -- <tarea>
  1. Descifra prompts (sops, llave de entorno) o los trae del repo privado.
  2. Snapshot git antes/después; corre `opencode run --agent`.
  3. Hashea inputs/outputs, arma el recibo, lo firma (Ed25519/HMAC con llave
     de entorno) y lo deja en `docs/specs/.working/<inc>-receipts/`.
```

La llave vive en Codespaces secrets (devs internos) o environment secrets
(CI, tras aprobación). El proveedor jamás la ve; sin ella no hay firma
válida aunque copie el wrapper.

### 3.3 Verificador determinista: check `attest-verify` (requerido)

Con la **llave pública en el repo**, sin secretos ni LLM:

1. Firma válida y `nonce` corresponde a una aprobación real (vía API).
2. `prompt_bundle` == versión de prompts esperada para ese commit.
3. Los hashes de `outputs` coinciden con el diff del PR (nada fuera del
   recibo, nada del recibo ausente).
4. Toda transición de estado del shared context tiene su recibo
   (cobertura completa: sin recibo no hay avance).

### 3.4 Nivel Sigstore (runs en CI)

Cuando el agente corre en Actions (fase 3), el workflow atesta el recibo
con `actions/attest@v4` (custom predicate) y el check exige además
`gh attestation verify`. Prueba criptográfica de **dónde y cómo** se
produjo, con transparencia corporativa (instancia privada, sin log público).

## 4. Diseño B: definiciones como secreto corporativo

Niveles, de menor a mayor sensibilidad:

| Nivel | Contenido | Dónde vive | Quién lo ve |
|---|---|---|---|
| L0 público | Este repo tal cual (salvo prompts) | repo de trabajo | todos |
| L1 corporativo | `core/agents/**`, skills propias | mismo repo **cifrado con sops+age** | wrapper con llave (devs internos, CI) |
| L2 alfa | Decisiones/contratos sensibles | **repos privados separados** | solo internos; al trabajo llega pack redactado |

Reglas:

1. **El proveedor nunca recibe la llave age.** Sin ella, L1 es ciphertext
   y el wrapper no corre en su entorno.
2. **L2 jamás entra a prompts ni a packs de proveedor.** El curator
   (lado confiable) genera packs con niveles `internal` vs `provider`.
3. **Lanes sensibles (`workspace`, fixes críticos) = ejecución remota.**
   El proveedor pide `/sdd implement`; corre en runner corporativo; él ve
   el PR + recibos, nunca los prompts.
4. **Lo enviado a un LLM público lo ve el proveedor del modelo.** Alfa
   nunca va en un prompt salvo tiers enterprise con no-entrenamiento
   contractual (política ya vigente en `opencode-harness.md`).
5. Rotación de llaves documentada; cada rotación re-cifra L1 y invalida
   recibos viejos (el `prompt_bundle` + nonces con expiración lo fuerzan).
6. NDA como capa legal complementaria, nunca como única defensa.

## 5. Qué cambia en este repo al implementar

- `tooling/foundry-attest` (wrapper) + `tooling/attest-verify.py` (check).
- `states.md`: recibo como artefacto de transición; firmas con autoría
  (ya previsto en la investigación anterior).
- `matrix.yaml`: niveles de pack (`internal`/`provider`) en context-curator;
  lanes sensibles marcados `remote-only`.
- `.sops.yaml` + prompts cifrados (migración L0→L1 por lotes).
- Workflows plantilla: `sdd-states`, `approval-proof`, `attest-verify`.

## 6. Decisiones abiertas

1. Custodio de llaves y política de rotación (¿maintainers + calendario?).
2. ¿Recibos exigidos en todos los carriles o solo `feature/workspace`?
   (recomendado: todos — el costo es un hash + una firma).
3. Segregación L2 ahora o cuando exista contenido alfa real.

## 7. Fuentes

- Docs GitHub: artifact attestations (conceptos + uso), secrets en Actions
  (patrón gpg/sops para secretos >48KB).
- actions/attest (README, modos, permisos).
- getsops/sops (age como método recomendado, `SOPS_AGE_KEY`).
