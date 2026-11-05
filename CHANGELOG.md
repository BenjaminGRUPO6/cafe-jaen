# Cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Cada versión
corresponde a la entrega de una iteración XP del plan v3.0/v4.0 (precio mundial en vivo y
recomendación de venta).

## [v1.12] — Kit visual, perfil visible, sesiones por pestaña y cuentas del equipo

### Agregado
- **Kit visual de Café Jaén**: nuevo logotipo en la cabecera, ícono de la app (PWA y favicon),
  portada en las pantallas de acceso, íconos propios en la barra inferior y en las pestañas del
  equipo, e ilustración para las bandejas sin mensajes. Se mantiene la paleta Cosecha.
- **Perfil visible**: debajo de la cabecera se ve con qué cuenta se ingresó (nombre o celular) y
  su cargo: «Administrador» o «Caficultor» (`GET /api/auth/me`). El registro pide el nombre.
- **Crear cuentas del equipo** desde «Participantes → Cuentas del equipo» con nombre, celular y
  contraseña; quedan activas al instante (`POST /api/admin/team`). Migración 0014 (nombre).

### Corregido
- Dos cuentas abiertas en pestañas del mismo navegador ya no se mezclan: cada pestaña guarda su
  propia sesión y una pestaña nueva entra con la última sesión usada.
- El equipo ya no ve «Ayuda» (responde en «Equipo → Mensajes»).

## [v1.11.1] — Arranque que no se bloquea

### Corregido
- Render canceló el despliegue de v1.11: la tarea de arranque que genera el pronóstico consultó
  una web que no respondió y la app no abrió su puerto en 15 minutos. Ahora la API arranca
  apenas terminan las migraciones y la cuenta del equipo; el histórico, el primer pronóstico y
  los datos de demostración se cargan en segundo plano, cada uno con tiempo máximo.
- Las consultas a Yahoo Finance tienen un tiempo máximo de 15 segundos.

## [v1.11] — Verificación por celular, ingreso con correo y «Atención»

### Cambiado
- El **correo es opcional** al registrarse. El código se envía con prioridad al **celular por
  WhatsApp** (WhatsApp Business, `WHATSAPP_TOKEN` y `WHATSAPP_PHONE_NUMBER_ID`) y, si no se
  puede, al correo (Brevo). Si ningún canal está configurado, el equipo lo envía con un toque:
  «Enviar código por WhatsApp» en «Participantes» abre su WhatsApp con el mensaje listo.
- En «Confirma tu cuenta», el botón «Pedir mi código por WhatsApp» escribe al equipo
  (`TEAM_WHATSAPP`).
- **Ingreso con celular o correo** en la misma casilla.
- Migración 0012: se guarda por qué canal salió cada código.

### Agregado
- **Atención al caficultor** (nuevo módulo hexagonal `support`): en «Ayuda» el caficultor
  escribe sus dudas y ve las respuestas, con aviso de respuestas nuevas en la cabecera. El
  equipo responde desde «Equipo → Mensajes» (primero las que esperan respuesta). Migración 0013.

## [v1.10] — Verificación por correo y administración de cuentas

### Agregado
- **Registro con correo y código de verificación**: al crear la cuenta llega un código de 6
  dígitos al correo (vence en 15 minutos, 5 intentos, reenvío cada minuto). Sin confirmarlo no
  se puede ingresar, así no quedan cuentas con celulares inventados. Pantalla «Confirma tu
  cuenta» (`/verificar`) y rutas `/api/auth/verify` y `/api/auth/resend`.
- **Respaldo del equipo**: si el correo no sale, el código aparece en «Equipo → Participantes»
  para enviarlo por WhatsApp.
- El correo se envía con la API de Brevo (`BREVO_API_KEY`, `EMAIL_SENDER`), porque el plan
  gratis de Render bloquea el envío por SMTP; en local también sirve Gmail por SMTP.
- **Eliminar cuentas** desde «Participantes»: su código de invitación queda libre y su sesión
  deja de servir. Nadie se elimina a sí mismo y siempre queda una cuenta del equipo.
- **Códigos del equipo** (`EQUIPO-…`) en «Códigos»: crean más cuentas de administrador.
- Migración 0011: las cuentas que ya existían quedan verificadas.

## [v1.9.1] — Gráfico con eje de tiempo real

### Corregido
- «Gráfico»: el eje usa el tiempo real. En 30 y 90 días las fechas quedan a intervalos parejos
  (cada lunes o cada 4 semanas) aunque los fines de semana no tengan precio; en «Hoy» las horas
  son redondas (cada 15, 30 o 60 minutos) aunque haya minutos sin consultas.
- «Hoy» dice la hora de la última cotización y cuántos minutos tiene de retraso (las webs
  gratuitas publican la bolsa con unos 10 minutos de retraso).

## [v1.9] — Dólar en vivo, gráfica de Jaén y contraseña visible

### Agregado
- **Dólar en vivo (USD/PEN) cada minuto** desde Yahoo Finance (PEN=X) o TradingView
  (FX_IDC:USDPEN), la primera que responda (`EXCHANGE_RATE_SOURCES`, migración 0010). El precio
  en soles, el gráfico de hoy y el historial usan el dólar de cada momento; si ninguna web
  responde, se usa el tipo de cambio oficial del BCRP del día.
- La pantalla Precio dice de dónde salió el dólar y a qué hora, con enlace a la fuente.
- «Precio estimado en Jaén» muestra la línea de hoy, minuto a minuto, en lugar del recuadro;
  el aviso de datos sintéticos queda como una nota debajo.
- Botón del ojo para ver u ocultar la contraseña al ingresar y al crear la cuenta.

### Cambiado
- «Equipo → Bolsa» ya no separa por tipo de café: la bolsa es una sola; cada fila muestra el
  dólar usado (con su fuente) y el estimado en Jaén de los tres tipos.

## [v1.8] — Cuatro webs reales evaluadas, fuentes con enlace y cooperativas de demostración

### Agregado
- Dos webs reales más de la bolsa de Nueva York: **CNBC** (@KC.1) y **TradingView**
  (ICEUS:KC1!). El Recolector consulta ahora Yahoo Finance, Stooq, CNBC y TradingView.
- «Equipo → Bolsa → Evaluación de fuentes del día»: puntaje de 0 a 100 por web
  (40 × respuesta + 40 × coincidencia con las demás + 20 × qué tan al día está) y la etiqueta
  «Mejor fuente» (`source_ranking.rank_sources`).
- Todas las fuentes se muestran como enlaces que abren su página: en el historial de la bolsa,
  en la evaluación y en la nota «Fuente:» del precio (también el BCRP).
- `DEMO_COOPERATIVES=true`: al arrancar (y luego cada 5 minutos hasta lograrlo) se cargan una
  sola vez los precios sintéticos «Cooperativa JAENPERU sintético A…F», así el estimado en Jaén
  y el pronóstico en Jaén muestran datos en la demostración.

### Corregido
- El historial ya no dice «las webs no coincidieron» cuando la bolsa solo repitió la misma
  cotización: cada consulta guarda su resultado (publicada, sin cambios, no publicada o sin
  datos) y el motivo real (migración 0009).
- Si aún no hay cierres diarios, los datos sintéticos usan el último precio real en vivo.
- Las webs que no informan la hora de la bolsa (TradingView) no adelantan la hora publicada.

## [v1.7.1] — Arranque a prueba de configuración antigua

### Corregido
- Si `QUOTATION_SOURCES` todavía decía «demo», la versión nueva no arrancaba y Render dejaba en
  línea la anterior, que siguió guardando precios sintéticos. Ahora las webs desconocidas se
  ignoran con un aviso en los Logs (sin ninguna válida se usan Yahoo Finance y Stooq).
- Migración 0008: vuelve a quitar los precios «DEMO» guardados después de la 0007.

## [v1.7] — Datos sintéticos de demostración, claramente marcados

### Agregado
- «Equipo → Cooperativas → Datos sintéticos para la demostración»: carga 6 cooperativas
  «Cooperativa JAENPERU sintético A…F» con unos 60 días de precios (≈ 650) calculados sobre el
  precio REAL de la bolsa de cada día; se vuelven a generar o se borran con un toque
  (`/api/admin/synthetic-data`, caso de uso `ManageSyntheticData`).
- El estimado en Jaén avisa cuántos de los precios usados son sintéticos.
- El precio de la bolsa, el tipo de cambio y el histórico siguen siendo solo reales.

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
