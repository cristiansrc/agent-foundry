---
name: accessibility-standard
description: Auditoría y diseño accesible WCAG 2.2 AA — criterios completos con verificación práctica (teclado, contraste, ARIA, targets táctiles, formularios), herramientas automatizadas y clasificación de severidad para bloquear releases.
---

# Skill: Accessibility Standard (WCAG 2.2 AA)

Estándar de accesibilidad obligatorio para toda interfaz nueva o modificada.
Complementa `ux-heuristics` (pre-check rápido); esta skill es la auditoría
profunda que puede BLOQUEAR un release.

## Nivel de cumplimiento

Target: **WCAG 2.2 nivel AA**. Clasificación de hallazgos:

| Severidad | Significado | Acción |
|-----------|-------------|--------|
| **Bloqueante** | Impide uso a personas con discapacidad (teclado roto, contraste crítico, sin labels) | No pasa validación |
| **Mayor** | Barrera significativa con alternativa dolorosa | Fix antes del release |
| **Menor** | Fricción accesible pero mejorable | Backlog |

## 1. Perceptible

- [ ] **Contraste texto**: ≥4.5:1 texto normal; ≥3:1 texto grande (≥24px o ≥18.66px bold).
- [ ] **Contraste componentes**: ≥3:1 en iconos, bordes de inputs, indicadores de foco, estados de gráficos.
- [ ] **No usar solo el color** para transmitir información (error = color + icono + texto).
- [ ] **Alternativas textuales**: toda imagen funcional tiene alt que describe su función; decorativas `alt=""`.
- [ ] **Reflow**: usable a 320px de ancho sin scroll horizontal (excepto tablas de datos).
- [ ] **Zoom 200%**: sin pérdida de contenido ni funcionalidad.

## 2. Operable — teclado primero

- [ ] **Todo alcanzable por teclado**: menús, modals, tabs, drag&drop, date pickers.
- [ ] **Sin trampas de teclado**: siempre hay salida con Esc/Tab de cualquier componente.
- [ ] **Foco visible**: indicador ≥3:1 contra fondo adyacente; jamás `outline: none` sin reemplazo.
- [ ] **Focus Not Obscured (2.2)**: al navegar, el elemento enfocado no queda tapado por headers/banners sticky.
- [ ] **Skip link** ("saltar al contenido") como primer elemento tabbeable.
- [ ] **Orden de tab lógico**: sigue el orden visual de lectura.
- [ ] **Target Size mínimo (2.2)**: targets ≥24×24px CSS (ideal 44×44); excepciones solo inline-text e equivalentes.
- [ ] **Arrastrables tienen alternativa (2.2)**: todo drag&drop ofrece click/teclado/botones.
- [ ] **Timers ajustables**: extender/desactivar límites de tiempo; sin autoplay de más de 5s sin control.
- [ ] **Atajos de solo-carácter se pueden desactivar o remapear**.

## 3. Comprensible

- [ ] **Idioma declarado**: `<html lang="es">` correcto.
- [ ] **Labels persistentes**: placeholder NO es label; label visible asociado (`for`/`id`) o `aria-label`.
- [ ] **Errores identificables**: campo inválido con texto específico + sugerencia + `aria-describedby`.
- [ ] **Navegación consistente**: mismo orden/menús en todas las páginas.
- [ ] **Redundant Entry (2.2)**: no pedir re-ingresar información ya dada en el mismo proceso (checkout, multi-step).
- [ ] **Auth accesible (2.2)**: login sin test cognitivo (memorizar/transcribir) — permite password managers y paste.

## 4. Robusto

- [ ] **Semántica antes que ARIA**: `<button>` > `<div role="button">`; HTML nativo gana siempre.
- [ ] **Name/Role/Value** correctos en controles custom (combobox, tabs, modals).
- [ ] **Modals**: focus trap + retorno del foco al cerrar + `aria-modal` + título referenciado.
- [ ] **Status messages**: cargas/resultados dinámicos con `role="status"` / `aria-live="polite"` (resultados urgentes: `assertive`).
- [ ] **ARIA nunca rompe**: cada atributo ARIA cumple su contrato (no aria-label redundante con texto visible).

## Verificación automatizada

```bash
# Auditoría completa (CI-friendly): 0 violaciones critical/serious permitidas
npx axe-cli <url> --exit

# Con dev server corriendo, en Puppeteer MCP:
#   inyectar axe-core y correr axe.run() por vista; reportar violaciones
npx pa11y-ci --config pa11y.json     # multi-página

# Contraste puntual: calcular ratio de los pares fg/bg del tema
```

Reglas del pipeline:

1. `axe-core` sin violaciones `critical` ni `serious` = condición de done de UI.
2. Lo automatizado cubre ~40%: la lista de checkboxes de arriba requiere revisión manual.
3. Prueba de teclado real: recorrer TODA la pantalla crítica sin tocar mouse.

## Integración con el flujo SDD

- **ui-designer**: diseña cumpliendo §1–§3 desde el artboard (contraste en tokens,
  targets, estados de foco visibles en el diseño).
- **functional-tester-agent**: ejecuta axe-core por vista en su suite E2E +
  recorrido de teclado manual documentado.
- **final-validation**: verifica 0 violaciones bloqueantes como criterio de
  calidad junto a cobertura de tests.

## Reporte de hallazgos

Formato por hallazgo:

```
[Criterio WCAG 2.x.x] [Bloqueante|Mayor|Menor] <componente/vista>
Problema: <qué impide>
Evidencia: <screenshot/paso de reproducción>
Fix propuesto: <solución concreta>
```

Anti-patrones: "lo arreglamos con un modo accesible aparte", overlay de
accessibilidad de terceros como solución definitiva, aria-label en español
mientras la página está en inglés (o viceversa).
