# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Cada versión
corresponde a la entrega de una iteración XP del plan v3.0/v4.0 (precio mundial en vivo y
recomendación de venta).

## [v1.1] — Interfaz dinámica, pronóstico en Jaén y ejecución local en un paso

### Cambiado
- Herramientas del front-end fijadas a versiones que corren desde Node 20 (probado con Node
  22.11): Vite 6, Vitest 3, ESLint 9, jsdom 26 y vite-plugin-pwa 1; `dev.py` revisa la versión de
  Node y `setup` reinstala `node_modules` desde cero.

### Agregado
- HU06 (T38): la pantalla «7 días» muestra el **pronóstico estimado en Jaén** por tipo de café
  (pronóstico de la bolsa × porcentaje de las cooperativas), alineado con la ficha de la TPP.
- HU15 (T39, T40): interfaz v2 «Cosecha»: paleta de bloques vivos, Bricolage Grotesque +
  Atkinson Hyperlegible Next, barra inferior flotante y animaciones con Framer Motion (precio
  que rueda, línea del día, pastillas deslizantes, veredicto, rangos, chat y bloques de carga).
- HU16 (T41): `dev.py` multiplataforma (`setup`, `demo`, `start`, `test`, `check`, `admin`,
  `reset`), SQLite por defecto en local y `backend/.env` con secreto aleatorio.
- HU16 (T42): Dependabot, `.python-version`, `.nvmrc` y README con arquitectura, estructura y
  paso a paso.
- Datos de demostración con precios de cooperativas de ejemplo: el estimado en Jaén se ve sin
  pasos extra.

### Cambiado
- La pestaña «Pronóstico» de la barra inferior se llama «7 días» (entra en 360 px de ancho).
- `useApi` conserva el dato anterior de la misma ruta mientras recalcula.

## [v1.0] — Iteración 3 · MVP congelado para el experimento

### Agregado
- HU05: Agente Estratega de venta (módulo `decision`) con la regla «¿Vendo ahora o espero?»,
  `GET /api/decision/today`, pantalla «¿Vendo?» y herramienta del asesor.
- HU05: prueba retrospectiva de la regla (`scripts/backtest_selling_rule.py`, `make backtest`).
- HU10: Dockerfile, docker-compose, guía de operación y prueba de carga (Locust, 30 usuarios)
  más 30 flujos en vivo abiertos a la vez.
- HU11: manual de usuario y guía de inducción.
- HU12: **precio estimado en Jaén** por tipo de café (convencional, orgánico, especial): el equipo
  anota en la pantalla «Equipo» cuánto paga cada cooperativa; la app guarda la bolsa del momento
  y estima en vivo bolsa × mediana de los porcentajes de 30 días. Rol de administrador
  (`scripts/create_admin.py`) y migración `0003_local_prices_and_roles`.

### Corregido
- El registro verificaba la contraseña dos veces con bcrypt; ahora emite el token directamente
  (con 30 registros simultáneos bajó de 7 s a 2,5 s).

## [v0.2] — Iteración 2

### Agregado
- HU04: gráfico tipo bolsa (hoy minuto a minuto, 30 y 90 días) con carga diferida de la librería.
- HU06: Agente Predictor con ELM y modelo ingenuo con deriva; elige el de menor MAPE.
- HU08: Agente Asesor con herramientas, modelo por palabras clave, adaptador de Anthropic y
  salvaguarda contra números inventados; batería de 20 preguntas.
- HU09: letra mínima de 16 px, contraste AA, instalación como PWA y último precio sin conexión.
- Migración `0002_forecasts`.

### Corregido
- Conversión de un arreglo de NumPy a número en la ELM (incompatible con NumPy 2.5).
- Etiquetas de la navegación inferior subidas de 14,4 px a 16,2 px.

## [v0.1] — Iteración 1

### Agregado
- HU01: registro con código de invitación, consentimiento informado y sesión de 30 días.
- HU02: Agente Recolector que consulta **varias webs** del precio de la bolsa de Nueva York cada
  minuto (Yahoo Finance y Stooq), publica la mediana, descarta la web discrepante, respeta el
  horario de la bolsa y conserva el último valor válido; tipo de cambio del BCRP una vez al día.
- HU03: Agente Analista y **precio en vivo tipo bolsa** (`GET /api/prices/live` y flujo
  `GET /api/prices/stream` con Server-Sent Events).
- HU07: Agente Supervisor (LangGraph), protocolo `AgentMessage` y trazas.
- Migración `0001_users_prices_traces` (incluye `live_quotes`).

## [v0.0] — Iteración 0 (exploración)

### Agregado
- Estructura hexagonal, contratos de arquitectura (import-linter), CI, estándar de código.
- Metáfora del sistema, tarjetas CRC y decisiones de arquitectura 0001–0003 y 0006.
- Script del spike que compara las webs del precio mundial (retraso y diferencias).
