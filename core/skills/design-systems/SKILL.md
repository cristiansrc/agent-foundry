---
name: design-systems
description: Descubrimiento, uso y validación de design systems en el código — extraer tokens y componentes existentes para que los diseños nuevos nazcan consistentes con la UI real del producto.
---

# Skill: Design Systems

Asegura que cualquier diseño nuevo use el sistema visual REAL del repositorio,
no un sistema inventado. Equivalente al /design-sync de las herramientas
comerciales: sincroniza contexto visual repo → diseños.

## Paso 1 — Descubrir el sistema existente

Antes de diseñar, busca (en este orden):

1. **Tokens declarados**: `tailwind.config.*`, `tokens.*`, `theme.*`,
   variables CSS (`--color-*`, `--space-*`) en globals.css/styles.
2. **Librería de componentes**: carpeta `components/ui|common|shared` —
   inventaría botones, inputs, cards, modals, tablas con sus props/variantes.
3. **Escala tipográfica**: clases utilitarias o variables de font-size/weight/family.
4. **Espaciado y radios**: patrón dominante (grid 4px/8px, radius estándar).
5. **Modo oscuro**: estrategia existente (clase `.dark`, media query, tokens duales).

Documenta lo encontrado en `docs/designs/<increment>/design-context.md`:
inventario de tokens + componentes reutilizables con su ruta exacta.

## Paso 2 — Usar el sistema en los diseños

- Los artboards HTML deben declarar los tokens como variables CSS al inicio
  del `<style>`, con valores EXACTOS del repo:

```css
/* Tokens desde tailwind.config.js / :root */
--color-primary: #...;
--radius-card: 12px;
--font-body: ...;
```

- Componente existente que cubre una necesidad = ese componente (mismo layout
  y variantes), nunca una versión paralela "mejorada" sin consultar.
- Si una necesidad NO tiene componente ni token en el repo, márcala en el
  README del diseño como **propuesta nueva** (el humano decide si entra al
  sistema o se hace excepción local).

## Paso 3 — Validar consistencia antes de entregar

Checklist anti-inconsistencia:

- [ ] Todos los colores del artboard existen en el ramp del repo (o están propuestos)
- [ ] Tipografía usa la escala existente (sin tamaños intermedios arbitrarios)
- [ ] Espaciados múltiplos de la base (4/8px) — sin paddings "al ojo"
- [ ] Radios/sombras idénticos a los patrones vigentes
- [ ] Dark mode resuelto si el repo lo tiene (mismos roles semánticos)
- [ ] Sin dos grises compitiendo ni duplicados semánticos nuevos

## Diagnóstico de sistema roto

Si al extraer tokens encuentras contradicciones (dos grises primarios, escala
con huecos, dark mode incompleto): repórtalo en `design-context.md` como
hallazgo con severidad. No heredes el caos silenciosamente: el diseño puede
servir de diagnóstico del sistema documental.

## Repo sin sistema

Si no existe nada: declara tokens mínimos en el primer artboard (ramp de 10
colores, escala tipográfica 5 pasos, espaciado 4px, 2 radios) y proponlos en
el README como semilla de design system para aprobación humana.
