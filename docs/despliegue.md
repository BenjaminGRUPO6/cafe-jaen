# Despliegue y edición en línea

Para mostrar el software sin depender de una computadora local, lo publicamos de dos formas
gratuitas:

| Opción | Para qué la usamos | Costo |
|---|---|---|
| **Render** | App pública con una URL fija ([https://cafe-jaen-oa58.onrender.com](https://cafe-jaen-oa58.onrender.com)). Cada `git push` a `main` la vuelve a desplegar. | Gratis (plan *Free*) |
| **GitHub Codespaces** | El proyecto completo en el navegador: editamos el código y vemos el cambio en la app al instante. | Gratis (horas mensuales incluidas en la cuenta de GitHub) |

## 1. Render: app pública

### Cómo lo armamos

```
GitHub (main) ──push──► Render construye el Dockerfile de la raíz
                         ├─ etapa 1: node 22 compila el front-end (PWA)
                         └─ etapa 2: python 3.12 + API FastAPI que también entrega la app
                                    └─ scripts/start_server.sh
                                       migraciones → cuenta del equipo → histórico real → uvicorn
```

- **Un solo servicio y una sola URL:** la API (`/api/...`) y la app comparten dominio, así que no
  necesitamos CORS. La API entrega la app compilada cuando se define `STATIC_DIR`
  (`backend/src/shared/infrastructure/api/spa.py`).
- **Infraestructura como código:** `render.yaml` (Blueprint) declara el servicio y sus variables;
  el `JWT_SECRET` lo genera Render.
- **Solo datos reales:** la bolsa de Nueva York desde Yahoo Finance, Stooq, CNBC y TradingView, y el tipo de cambio
  del BCRP. Al arrancar se carga el histórico real de 5 años (si ya está, no se repite) y se
  genera el pronóstico. Si las webs no responden en ese momento, la API arranca igual y el
  Recolector vuelve a intentar cada minuto con la bolsa abierta.

### Cómo lo publicamos

1. Iniciamos sesión en <https://render.com> con la cuenta de GitHub dueña del repositorio.
2. **New +** → **Blueprint** → elegimos el repositorio y le damos acceso a la GitHub App de Render.
3. Render leyó `render.yaml` y propuso el servicio `cafe-jaen`; lo creamos con **Deploy Blueprint**.
4. El primer build tardó unos minutos. En los *Logs* se ve el arranque:

   ```
   Cuenta del equipo 9XXXXXXXX: creada.
   Histórico real: 1255 cierres diarios (Yahoo Finance) · 1238 tipos de cambio del BCRP
   Recolección: {'market_open': True, 'quotation_saved': True, 'sources_ok': ['Yahoo Finance', 'Stooq'], …}
   Pronóstico generado: True
   Uvicorn running on http://0.0.0.0:10000
   ==> Your service is live
   ```

5. Con el servicio en **Live**, entramos con la cuenta del equipo, generamos códigos en
   «Equipo → Códigos» y con ellos se registran los caficultores (cada código sirve una vez).

### Cuenta del equipo y datos permanentes

El plan gratuito de Render no tiene terminal, así que la cuenta de administrador no se crea con
`python dev.py admin`. La creamos con dos variables que el servicio lee al arrancar
(`backend/scripts/ensure_admin.py`); si la cuenta ya existe, no la toca:

| Variable (Render → *Environment*) | Valor |
|---|---|
| `ADMIN_PHONE` | Celular del equipo, 9 dígitos que empiezan con 9 |
| `ADMIN_PASSWORD` | Contraseña de al menos 8 caracteres |
| `DATABASE_URL` | URL de la base PostgreSQL gratuita de Neon (`postgresql://…?sslmode=require`) |

Con esa cuenta aparece en la app el enlace **«Equipo»** con cinco pestañas:
- **Precios:** anotamos lo que paga cada cooperativa (y corregimos o borramos un dato mal
  escrito); el «Precio estimado en Jaén» se recalcula al instante.
- **Cooperativas:** catálogo con las cooperativas de Jaén; agregamos, editamos o archivamos. Al
  archivar una que ya tiene precios, sus datos se conservan para no perder el historial. Aquí
  también cargamos o borramos los **datos sintéticos para la demostración** (6 cooperativas
  «Cooperativa JAENPERU sintético A…F» con unos 60 días de precios sobre la bolsa real).
- **Códigos:** generamos códigos de invitación para el GE y borramos los que no se usaron.
- **Participantes:** quiénes del GE se registraron, con qué código, cuándo y su último ingreso.
  Se actualiza sola cada 10 segundos.
- **Bolsa:** historial minuto a minuto (se guarda siempre; se elige el día) con el precio
  publicado, el estimado en Jaén del tipo de café elegido y, en «Ver fuentes», lo que marcó
  cada web: usada, descartada (se alejó más de 1 % de la mediana) o sin respuesta.

Los caficultores no ven «Equipo» y la API les responde 403 si intentan entrar.

**Base de datos permanente (Neon, gratis):** creamos un proyecto en <https://neon.tech>, copiamos
la *connection string* y la pegamos en `DATABASE_URL`. Al arrancar, la app crea las tablas sola
(migraciones de Alembic), carga el histórico real una sola vez y crea la cuenta del equipo.
Desde ahí, los registros sobreviven a los reinicios y a los despliegues. La misma base se puede
abrir desde el panel de Neon (*Tables*) para ver los usuarios en tiempo real.

### Limitaciones del plan gratuito

- **Se duerme** tras unos 15 minutos sin visitas; la primera visita después tarda alrededor de
  1 minuto en despertar. Antes de una presentación, abrimos la URL 2–3 minutos antes.
- **Sin `DATABASE_URL`, los datos se reinician** en cada despliegue o al despertar, porque SQLite
  vive dentro del contenedor. Con la base de Neon (sección anterior) son permanentes.
- **Horario de la bolsa:** el precio solo cambia de lunes a viernes de 04:15 a 13:30 (hora de
  Nueva York). Fuera de ese horario la app muestra el último precio real con «Bolsa cerrada».
- **Webs gratuitas:** Yahoo Finance a veces limita las consultas desde servidores en la nube.
  Si eso pasa, el Recolector sigue con Stooq; en «Equipo → Bolsa» se ve qué web no respondió.

### Cómo actualizamos la app publicada

```
git add .
git commit -m "feat(...): descripción"
git push
```

Render detecta el push y despliega solo (pestaña **Events** del servicio). Si el build falla, la
versión anterior sigue en línea.

## 2. GitHub Codespaces: edición en tiempo real

Configuramos `.devcontainer/` para que el proyecto se abra listo en el navegador:

1. En GitHub: **Code** → pestaña **Codespaces** → **Create codespace on main**.
2. Se abre VS Code en el navegador y la primera vez instala todo solo (`python dev.py setup` y
   `python dev.py datos`), en unos 5 minutos.
3. En la terminal: `python dev.py start`. La app se abre en otra pestaña (puerto 5173).
4. Al editar, por ejemplo, `frontend/src/shared/texts/es.ts` o `frontend/src/shared/styles.css` y
   guardar, la app se actualiza al instante sin recargar.
5. Para mostrarla a otra persona: pestaña **Ports** → clic derecho en 5173 → **Port Visibility** →
   **Public**, y se comparte esa URL mientras el codespace esté abierto.
6. Al terminar: **Code** → **Codespaces** → detener el codespace para no gastar horas.

Los cambios hechos en el codespace se guardan con `git add`, `git commit` y `git push`, igual que
en local; ese push también actualiza la app publicada en Render.

## Cooperativas de demostración (v1.8)

Con `DEMO_COOPERATIVES=true` la app carga una sola vez los precios **sintéticos** «Cooperativa
JAENPERU sintético A…F» en cuanto tiene el precio real de la bolsa (al arrancar o, si todavía no
lo tiene, reintentando cada 5 minutos). La bolsa y el tipo de cambio siguen siendo reales. Antes
del experimento con caficultores ponemos `DEMO_COOPERATIVES=false` y los borramos en
«Equipo → Cooperativas».

## Verificación por correo (v1.10)

Al registrarse, cada persona recibe un código de 6 dígitos en su correo y debe escribirlo para
entrar. El plan gratis de Render bloquea el envío por SMTP (puertos 25, 465 y 587), por eso el
correo sale por la API de **Brevo** (gratis hasta 300 correos al día):

1. Creamos una cuenta gratis en https://www.brevo.com con nuestro Gmail.
2. En Brevo → *Senders, domains & dedicated IPs* → *Senders* agregamos ese Gmail como remitente y
   lo confirmamos con el enlace que llega al correo.
3. En Brevo → *SMTP & API* → *API keys* creamos una clave.
4. En Render → *Environment* agregamos `BREVO_API_KEY` (la clave) y `EMAIL_SENDER` (el Gmail
   verificado) y guardamos con *Save, rebuild, and deploy*.

Si el correo no sale (sin clave, límite diario o caída de Brevo), la app no se bloquea: el código
aparece en «Equipo → Participantes» y se lo enviamos al caficultor por WhatsApp. En local
también se puede usar Gmail por SMTP con una «contraseña de aplicación» (`SMTP_USER`,
`SMTP_PASSWORD`).
