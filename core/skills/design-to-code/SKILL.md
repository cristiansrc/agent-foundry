---
name: design-to-code
description: Traducción fiel de un artefacto de diseño aprobado (HTML en docs/designs/) a componentes reales del stack destino, con verificación visual automatizada — el puente entre la dirección elegida y el executor.
---

# Skill: Design to Code

Convierte una dirección de diseño APROBADA en código de producción sin
reinterpretarla. El artefacto aprobado manda; este documento define cómo
traducirlo y cómo verificar que el resultado lo respeta.

## Entradas obligatorias

Antes de implementar verifica que existen:

1. `docs/designs/<increment-name>/<x>-<slug>.html` — la dirección ELEGIDA.
2. La decisión registrada en su README (`## Decisión de diseño` con elección).
3. El stack destino confirmado por el humano (React+Vite+TS, Next.js,
   HTML/CSS/JS plano u otro).

Si falta cualquiera: `Blocked: design artifact not approved`.

## Reglas de traducción

- **Layout, jerarquía y espaciado** del artboard se reproducen 1:1 salvo
  imposibilidad técnica documentada (registrarla en el task board).
- **Tokens**: usa las variables del design system del repo; si el artboard
  declara tokens propios en comentarios, promuévelos al sistema (no los
  hardcodees por componente).
- **Componentización**: cada bloque repetido del artboard = componente;
  estados incluidos en el diseño (hover, vacío, error) = variantes/props.
- **Interacciones del modo clickeable** del artboard definen el comportamiento
  mínimo navegable: rutas/transiciones que el prototipo tenía deben existir.
- **Responsive**: si el artboard incluye variante móvil, implementa breakpoints
  equivalentes; no inventes comportamientos móviles no diseñados (consulta).
- No "mejores prácticas" estéticas no presentes en el diseño: si algo te parece
  mejorable, propónlo DESPUÉS como incremento separado.

## Verificación visual obligatoria (self-test loop)

Tras implementar, antes de reportar done:

1. Compila y pasa typecheck del stack.
2. Levanta el dev server.
3. Con Puppeteer MCP (o equivalente): navega cada pantalla implementada,
   compara contra el artboard lado a lado (screenshot vs archivo local).
4. Ejecuta los estados diseñados (vacío, error, hover) y confirma que existen.
5. Reporta en el task board: archivos creados + screenshots de verificación.

Discrepancias menores (<4px, antialiasing) se toleran; diferencias de
estructura/jerarquía NO: corrige o bloquea.

### Bucle Gauntlet acotado (para pantallas con barra de referencia)

Cuando la comparación visual requiera iteración (fidelidad al artboard), se
usa el bucle builder/crítico — acotado para no quemar tokens:

- **Barra tangible**: el artboard elegido (`docs/designs/<increment-name>/`)
  + screenshot del candidato capturado a la MISMA resolución. Sin barra
  tangible no hay gauntlet: se aplica solo el self-test lineal de arriba.
- **Crítico fresco**: subagente distinto del implementador, que SOLO compara
  bar vs candidato y NUNCA edita código.
- **Un gap por ronda**: el crítico devuelve el ÚNICO mayor gap, falsificable y
  medible ("gap card-header es 16px; artboard 32px", "jerarquía: CTA pierde
  peso visual"). Prohibido "se ve mal" o listas de 10 items.
- **Rondas**: máximo 5 (default). El builder cierra el gap indicado y se
  recaptura.

**Condiciones de parada (verificar TODAS cada ronda):**

| Condición | Acción |
|---|---|
| Crítico verdict: iguala o supera la barra | done + tabla de rondas |
| Cap de rondas alcanzado | escalar humano con gap abierto registrado |
| Mismo gap 2 rondas seguidas | parar: el builder no puede cerrarlo; escalar |
| Ronda rompe un stream verde (tests) | revertir cambio de esa ronda; parar |

Reporte final en task board: tabla ronda/gap/acción/verdict + screenshots lado
a lado. El crítico jamás hereda contexto del builder (contexto fresco = juicio
independiente); prohibido lanzar procesos detached dentro del crítico.

## Cambios de diseño a mitad de implementación

Si durante el build surge una razón válida para cambiar el diseño aprobado:
detente, actualiza el artboard con la propuesta, pide re-aprobación humana.
Nunca cambies código y diseño silenciosamente por caminos distintos.
