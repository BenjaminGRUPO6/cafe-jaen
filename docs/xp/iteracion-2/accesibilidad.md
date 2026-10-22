# Verificación de accesibilidad (T25, PA-09-1)

**Fecha:** 21/10/2026 (actualizada para la v3.0) · **Responsable:** Reyes Guerrero, L. B.

## Tamaño de letra

| Elemento | Tamaño | ¿≥ 16 px? |
|---|---|---|
| Texto base (`:root`) | 18 px | Sí |
| Precio en vivo | 46,8 px | Sí |
| Recomendación (Vender ahora / Esperar / …) | 28,8 px | Sí |
| Etiqueta «En vivo» | 16,2 px en negrita | Sí |
| Texto secundario (`.muted`, fuente, fechas) | 16,2 px | Sí |
| Etiquetas de la navegación inferior | 16,2 px (antes 14,4 px: corregido) | Sí |
| Campos de formulario y botones | 19,8 px | Sí |

## Contraste (WCAG 2.1, nivel AA exige ≥ 4,5 : 1)

Calculado con la fórmula de luminancia relativa de WCAG sobre los colores de `styles.css`.

| Elemento | Texto | Fondo | Contraste | AA |
|---|---|---|---|---|
| Texto general | #1b1b1b | #faf7f5 | 16,1 : 1 | ✔ |
| Precio y títulos | #3e2723 | #ffffff | 13,8 : 1 | ✔ |
| Encabezado y botón principal | #ffffff | #3e2723 | 13,8 : 1 | ✔ |
| Texto secundario y navegación inactiva | #5f5f5f | #ffffff | 6,4 : 1 | ✔ |
| «Subió» (verde) | #2e7d32 | #ffffff | 5,1 : 1 | ✔ |
| «Bajó» (rojo) | #c62828 | #ffffff | 5,6 : 1 | ✔ |
| Aviso sin conexión | #5d4300 | #fff3cd | 8,4 : 1 | ✔ |
| Burbuja del caficultor | #ffffff | #6d4c41 | 7,6 : 1 | ✔ |
| Etiqueta «En vivo» | #ffffff | #c62828 | 5,6 : 1 | ✔ |
| «Esperar» (azul) | #1565c0 | #ffffff | 5,7 : 1 | ✔ |
| «Vender ahora» y «Bolsa abierta» (verde) | #2e7d32 | #ffffff | 5,1 : 1 | ✔ |

El sube/baja no depende solo del color: también lleva flecha (▲/▼) y la palabra «Subió»/«Bajó».

## Navegación

- El precio en vivo es la pantalla inicial: **0 toques** después de ingresar; se actualiza solo.
- «¿Vendo ahora o espero?» está a **1 toque** (botón bajo el precio y barra inferior).
- Cualquier otra pantalla está a **1 toque** desde la barra inferior (máximo exigido: 2).

## Pendiente con usuarios reales (PA-09-1)

Prueba con al menos 3 caficultores o con el Cliente: ¿encuentran el precio sin ayuda? Registrar
el resultado aquí.

| Participante | ¿Encontró el precio sin ayuda? | Observaciones |
|---|---|---|
| | | |
| | | |
| | | |
