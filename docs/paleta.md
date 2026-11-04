# Diseño de la interfaz (v2 «Cosecha»)

Bloques de color vivos, letra grande y alto contraste para usar el celular en la chacra. La
referencia de estilo fueron las plantillas *fintech* «amigables» del Marketplace de Framer
(colores brillantes, tipografía expresiva y animaciones con resorte) en lugar del clásico
panel oscuro de bolsa; los colores salen del café: el grano dorado, el brote verde-lima del
cafeto, la cereza madura y el espresso. Cada color tiene **un solo significado**.

| Nombre | Hex | Uso |
|---|---|---|
| Espresso | `#1A1208` | Texto, barra inferior, botones principales |
| Grano | `#FFC531` | Bloque del precio de la bolsa (lo más importante) y pestaña activa |
| Brote | `#C6F36B` | Bloque del precio estimado en Jaén y «Vender ahora» |
| Hoja | `#087443` | Sube, bolsa abierta |
| Cereza | `#C62A20` | Baja, «En vivo», errores |
| Cielo | `#2456D6` | «Esperar» y foco del teclado |
| Niebla | `#F4F4EF` | Fondo de las pantallas |
| Papel | `#FFFFFF` | Tarjetas y pastillas |
| Corteza | `#5F574D` | Texto secundario |
| Línea | `#E3E1D8` | Bordes y separadores |

Tonos claros de apoyo: Hoja clara `#E2F7C4`, Cereza clara `#FFE1DC`, Cielo claro `#DDE7FF`.

## Contraste (WCAG 2.1)

| Combinación | Contraste | Nivel |
|---|---|---|
| Espresso sobre Grano (precio) | 11,7 : 1 | AAA |
| Espresso sobre Brote (estimado Jaén) | 14,5 : 1 | AAA |
| Espresso sobre Niebla (texto general) | 16,8 : 1 | AAA |
| Papel sobre Espresso (botones, barra) | 18,5 : 1 | AAA |
| Hoja sobre Papel («Subió») | 5,9 : 1 | AA |
| Cereza sobre Papel («Bajó») | 5,6 : 1 | AA |
| Cielo sobre Cielo claro («Esperar») | 5,0 : 1 | AA |
| Texto de la barra inferior sobre Espresso | 12,2 : 1 | AAA |
| Corteza sobre Niebla (texto secundario) | 6,4 : 1 | AA |

## Tipografía

- **Bricolage Grotesque** (variable): títulos, precios y veredictos. Expresiva y con números
  grandes muy legibles.
- **Atkinson Hyperlegible Next** (variable): todo el texto. Creada por el Braille Institute para
  personas con baja visión; distingue bien 0/O, 1/l/I y 5/S al leer precios al sol.

Ambas van **dentro de la app** (paquetes `@fontsource-variable`) y se guardan para usarse sin
conexión. Ningún texto baja de 16 px (PA-09-1).

## Movimiento (Framer Motion)

| Animación | Cuándo | Por qué |
|---|---|---|
| Entrada escalonada de los bloques | Al abrir «Precio» | El único momento coreografiado: muestra el orden de lectura |
| Dígitos que ruedan + destello | Al llegar un precio nuevo | Hace visible el cambio sin recargar (HU03) |
| Línea del día que se dibuja | Al abrir «Precio» | Muestra la tendencia de hoy de un vistazo |
| Pastilla deslizante | Al tocar la barra inferior o un selector | Indica qué se eligió |
| Veredicto con impulso e ícono que gira | Al calcular «¿Vendo?» | Confirma la respuesta |
| Barras de rango que crecen | Al abrir «7 días» | Lee el rango del pronóstico |
| Burbujas y «escribiendo…» | En el asesor | Muestra que la pregunta se está respondiendo |
| Bloques de carga con brillo | Mientras llegan datos | Evita pantallas en blanco |

Si el celular tiene activado «reducir movimiento», todo esto se desactiva
(`MotionConfig reducedMotion="user"` y `prefers-reduced-motion` en CSS).
