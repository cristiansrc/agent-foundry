---
name: ui-design-exploration
description: Protocolo de exploración visual estilo canvas — genera 3-4 direcciones de diseño realmente distintas como artefactos HTML autocontenidos antes de escribir código de producción, con preguntas de clarificación, índice comparativo y decisión humana obligatoria.
---

# Skill: UI Design Exploration (diseño antes que código)

Imita el flujo de las herramientas de diseño-canvas: requerimiento → N
direcciones comparables → refinamiento → decisión humana → recién entonces
código. El objetivo es eliminar el rework por interpretar la UI directamente
en código.

## Regla número uno

NUNCA escribas código de producción de una pantalla sin haber presentado al
menos UNA dirección visual aprobada en `docs/designs/`. La única excepción:
ajustes triviales de UI ya existente (cambiar un texto, un padding).

## Paso 1 — Clarificación obligatoria (antes de diseñar)

Pregunta SIEMPRE, en una sola ronda compacta:

1. **Modo**: ¿mockup estático o prototipo clickeable?
2. **Direcciones**: ¿propongo 3-4 direcciones distintas, o hay una referencia
   (marca, app, screenshot, design system) a seguir?
3. **Alcance**: ¿qué pantallas/estados entran? (listado, detalle, vacío, error...)
4. **Restricciones**: ¿stack destino conocido? ¿dark mode? ¿mobile-first?

Si el usuario ya respondió alguna en su pedido, no la repitas.

## Paso 2 — Generar direcciones

- Produce **3 direcciones por defecto** (2-4 según lo acordado) genuinamente
  distintas entre sí: jerarquía, densidad, tipografía y lenguaje visual
  diferentes — NO variaciones de color del mismo layout.
- Nombra cada dirección `a-<slug>.html`, `b-<slug>.html`, `c-<slug>.html`
  (ej.: `a-terminal-denso.html`, `b-editorial-limpio.html`, `c-industrial-noc.html`).
- Cada archivo es **un HTML autocontenido**: CSS inline en `<style>`, cero
  dependencias externas obligatorias, abre directo en el navegador.
  - Modo estático: composición fiel con datos de ejemplo realistas.
  - Modo clickeable: vanilla JS inline para navegación entre vistas/estados.
- Incluye las variantes acordadas lado a lado (desktop + móvil; light + dark)
  usando wrappers CSS grid etiquetados.
- Si el repo tiene design system/tokens, aplícalos (ver skill `design-systems`);
  si no existe, declara los tokens usados en comentarios del `<style>`.

## Paso 3 — Índice comparativo

Crea `docs/designs/<increment-name>/README.md` con una tabla:

| Dirección | Archivo | Lenguaje visual | Pros | Contras |
|-----------|---------|-----------------|------|---------|

Y una sección final `## Decisión de diseño` con el placeholder:

```markdown
## Decisión de diseño
Elegida: <pendiente — se firma junto al Gate 1>
Justificación: <la escribe el humano>
```

## Paso 4 — Presentación y espera

- Describe cada dirección en el chat en 2-3 líneas (lenguaje visual, cuándo
  conviene). NO elijas tú: la selección es humana.
- Ofrece mezclar elementos entre direcciones ("de A toma la tabla, de B el header").
- Detente. La decisión queda registrada en el README y se firma con el Gate 1.

## Contrato de handoff a implementación

Cuando el humano apruebe una dirección, el artefacto elegido es FUENTE DE
VERDAD para el executor (ver skill `design-to-code`): layout, jerarquía,
tokens, estados incluidos. Cambiar el diseño durante implementación = volver
a esta skill, no improvisar en código.

## Anti-patrones

- Una sola dirección sin pedir criterio.
- Direcciones gemelas que solo cambian el color primario.
- Dependencias externas obligatorias (CDN de fuentes/JS) que rompen el modo offline.
- Escribir componentes React/Vue "para ahorrar un paso": eso viola la regla uno.
- Elegir tú mismo la dirección ganadora.
