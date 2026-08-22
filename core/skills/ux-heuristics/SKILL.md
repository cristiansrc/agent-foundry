---
name: ux-heuristics
description: Heurísticas de usabilidad aplicadas — Nielsen accionable, estados de interacción obligatorios, UX writing, formularios y accesibilidad rápida para revisar o diseñar cualquier interfaz.
---

# Skill: UX Heuristics

Checklist accionable para diseñar o auditar interfaces. Úsala al generar
direcciones (ui-design-exploration), al revisarlas, y antes de dar por
terminada una pantalla.

## Las 10 heurísticas, versión accionable

1. **Visibilidad del estado**: toda acción lenta muestra progreso; toda acción
   exitosa confirma; toda falla explica qué pasó y qué hacer.
2. **Correspondencia con el mundo real**: etiquetas del dominio del usuario,
   no del modelo técnico ("Pacientes", no "Registros entidad_persona").
3. **Control y libertad**: acciones destructivas tienen undo o confirmación;
   siempre hay salida clara (cancelar/cerrar/volver).
4. **Consistencia**: misma acción = mismo componente en toda la app; un solo
   verbo por concepto (no mezclar "Eliminar"/"Borrar"/"Quitar").
5. **Prevención de errores**: deshabilita sobre valida (botón inactivo hasta
   formulario válido); restricciones de formato visibles antes de escribir.
6. **Reconocer > recordar**: no pedir memorizar datos de una pantalla a otra;
   contexto visible en cada vista (breadcrumbs, resúmenes).
7. **Flexibilidad**: atajos para expertos sin ocultar el camino largo para novatos.
8. **Estética minimalista**: cada elemento visible justifica su existencia;
   lo secundario colapsa (acordeones, tabs, "mostrar más").
9. **Recuperación de errores**: mensaje específico + causa + siguiente paso;
   jamás códigos crudos ni "algo salió mal".
10. **Ayuda centrada en la tarea**: documentación contextual donde duele,
    no manual lejano.

## Estados de interacción OBLIGATORIOS

Toda pantalla/colección de datos debe diseñar (o heredar) estos estados:

- **Vacío** (sin datos aún): qué ve el usuario primera vez + CTA principal.
- **Cargando**: skeleton > spinner si tarda >300ms.
- **Error** (red/servidor): retry accesible, estado conservado.
- **Parcial** (algunos datos fallan): mostrar lo que sí llegó + qué falló.
- **Sin permiso**: explicación y cómo obtener acceso.
- **Offline** (si aplica): qué funciona sin red.

Un diseño que solo muestra el happy path está INCOMPLETO.

## Formularios

- Labels arriba del campo (mejor que placeholder como label); placeholder solo
  para ejemplo de formato.
- Validar al blur, no en cada tecla; errores junto al campo con texto específico.
- Un solo botón primario por formulario; Enter envía; campos requeridos marcados.

## UX Writing

- Botones con verbo + objeto ("Guardar cambios" > "OK").
- Errores en voz activa, sin culpar al usuario ("No pudimos conectar" > "Conexión inválida").
- Vacíos con personalidad moderada + acción sugerida.

## Accesibilidad mínima (pre-check, profundiza accessibility-standard)

- Contraste texto ≥4.5:1 (≥3:1 texto grande) — verificar con herramienta.
- Targets táctiles ≥44×44px; focus visible siempre.
- Jerarquía semántica: h1→h2→h3 sin saltos; landmarks (nav/main/footer).

## Auditoría exprés (5 min)

Al revisar cualquier pantalla recorre: ¿estados completos? ¿error recovery?
¿consistencia de verbos/componentes? ¿contraste? ¿mobile usable? Documenta
hallazgos como hallazgos con severidad, no como opiniones.
