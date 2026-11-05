# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Cada versión
corresponde a la entrega de una iteración XP del plan v3.0/v4.0 (precio mundial en vivo y
recomendación de venta).

## [v1.6] — Solo datos reales

### Cambiado
- La app trabaja **solo con datos reales** ([decisión 0010](docs/decisiones/0010-solo-datos-reales.md)):
  Yahoo Finance y Stooq para la bolsa de Nueva York y el BCRP para el tipo de cambio. Se
  eliminaron la fuente sintética, las tres webs simuladas y el script de datos de demostración.
- Al arrancar en Render se carga el histórico real de 5 años (Yahoo Finance y, si no responde,
  Stooq) y se genera el pronóstico; en local, `python dev.py datos`.
- `dev.py`: `datos` reemplaza a `demo`, `start` usa siempre precios reales y `codigos N` genera
  códigos de invitación.

### Eliminado
- Migración 0007: quita de las bases existentes lo que generó la demostración (fuentes «DEMO …»,
  «Cooperativa Demo N», sus pronósticos y los códigos DEMO sin usar). Conserva usuarios,
  cooperativas reales, precios anotados por el equipo y datos reales.
- Resultados de la evaluación de modelos y de la prueba retrospectiva calculados con datos
  sintéticos: quedan pendientes de recalcular con el histórico real.

## [v1.5] — Historial de la bolsa con el detalle de cada web

### Agregado
- Cada consulta del Recolector queda registrada (migración 0006: `price_collections` y
  `source_readings`), se publique o no: lo que marcó cada web, su distancia a la mediana y si
  fue usada, descartada o quedó sin respuesta.
- «Equipo → Bolsa»: historial minuto a minuto por día, con «Ver fuentes» en cada fila, resumen
  del día y la nota «¿Cómo se elige el precio?».
- Modo demostración con tres webs sintéticas que compiten (a veces una se descarta o no responde).

### Cambiado
- Las 5 pestañas de «Equipo» siempre visibles en celular y PC (dos filas).

## [v1.4] — Transparencia, cooperativas de Jaén y gestión desde «Equipo»

### Agregado
- **Fuentes** en «Precio» para caficultores y equipo: enlaces a ICE (contrato café C), Yahoo
  Finance (KC=F), Stooq (KC.F) y el tipo de cambio del BCRP.
- Botón **«¿Cómo se calcula?»** con la fórmula y los números del momento en el precio por quintal,
  el estimado en Jaén, el pronóstico a 7 días y «¿Vendo ahora o espero?».
- Catálogo de **cooperativas de Jaén** (migración 0005): CENFROCAFE, Sol & Café, Jesús Solidario,
  Perú Andino y Café del Norte (fuentes públicas: JNC/Agraria.pe, Coop Coffees, Oikocredit y el
  registro de certificación orgánica de OCIA). Los nombres que ya tenían precios se agregan solos.
  Los precios de demostración siguen asignados solo a «Cooperativa Demo 1–3».
- En «Precio», el estimado en Jaén se ve **general** o **por cooperativa**.
- Asesor: catálogo de preguntas frecuentes con más de 20 temas (pergamino, quintal, horario de la
  bolsa, tipo de cambio, cooperativas, cómo se calcula, privacidad, instalar la app…).
- «Equipo» con cinco pestañas: Precios (corregir y borrar), Cooperativas (agregar, editar,
  archivar), Códigos (generar y borrar los libres), Participantes y Bolsa (historial de 24 h por
  tipo de café).

## [v1.3] — El equipo trabaja en la app publicada

### Agregado
- Cuenta del equipo creada al arrancar desde `ADMIN_PHONE` y `ADMIN_PASSWORD`
  (`scripts/ensure_admin.py`, caso de uso `EnsureAdmin`): en Render no hace falta terminal.
- Pestaña **«Participantes»** en «Equipo» (`/equipo/participantes`, solo administrador): quiénes
  del GE se registraron, con qué código, cuándo y su último ingreso; se actualiza cada 10 s.
- `GET /api/admin/participants` (caso de uso `ListParticipants`) y migración 0004 con la fecha
  del último ingreso (`last_login_at`).
- Base de datos permanente con PostgreSQL gratuito (Neon) en `DATABASE_URL`; la URL que entrega
  Neon se acepta tal cual (`postgres://` o `postgresql://`).

## [v1.2] — App publicada en línea y edición en el navegador

### Agregado
- Despliegue gratuito en **Render** de un solo servicio: `Dockerfile` de dos etapas (compila la PWA
  y la entrega desde la API), `render.yaml` (Blueprint) y `backend/scripts/start_server.sh`
  (migraciones → datos de demostración → API). Cada `git push` a `main` vuelve a desplegar.
- La API sirve la app compilada cuando se define `STATIC_DIR` (`shared/infrastructure/api/spa.py`),
  con respaldo a `index.html` para las rutas del front-end y 404 para las rutas `/api` desconocidas.
- **GitHub Codespaces** (`.devcontainer/`): el proyecto listo en el navegador para editar y ver los
  cambios al instante.
- Guía [docs/despliegue.md](docs/despliegue.md).

### Cambiado
- `seed_demo_data.py` es idempotente y crea los códigos `DEMO-0001` a `DEMO-0010`.
- Vite acepta las URL de Codespaces y redirige `/api` a `127.0.0.1:8000`.

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
- HU12: **precio estimado en Jaén** por tipo de café (convencional, orgánico, especial): nosotros
  anotamos en la pantalla «Equipo» cuánto paga cada cooperativa; la app guarda la bolsa del momento
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
