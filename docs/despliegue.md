# Despliegue y edición en línea

Dos formas gratuitas de mostrar el software sin depender de una computadora local.

| Opción | Para qué sirve | Costo |
|---|---|---|
| **Render** | App pública con una URL fija (por ejemplo `https://cafe-jaen.onrender.com`; Render muestra la exacta). Cada `git push` a `main` la vuelve a desplegar. | Gratis (plan *Free*) |
| **GitHub Codespaces** | El proyecto completo en el navegador: editar el código y ver el cambio en la app al instante. | Gratis (horas mensuales incluidas en la cuenta de GitHub) |

## 1. Render: app pública

### Cómo está armado

```
GitHub (main) ──push──► Render construye el Dockerfile de la raíz
                         ├─ etapa 1: node 22 compila el front-end (PWA)
                         └─ etapa 2: python 3.12 + API FastAPI que también entrega la app
                                    └─ scripts/start_server.sh
                                       migraciones → datos demo → uvicorn
```

- Un solo servicio y una sola URL: la API (`/api/...`) y la app comparten dominio, sin CORS.
- `render.yaml` (Blueprint) declara el servicio y sus variables; `JWT_SECRET` lo genera Render.
- Modo demostración: precio sintético que se mueve todo el día y códigos **DEMO-0001 a DEMO-0010**.

### Pasos (una sola vez, unos 10 minutos)

1. Entrar a <https://render.com> → **Get Started** → **Sign in with GitHub** con la cuenta dueña del
   repositorio.
2. **New +** → **Blueprint** → elegir el repositorio `cafe-jaen-sistema` (si no aparece:
   **Configure GitHub App** y darle acceso a ese repositorio).
3. Render lee `render.yaml` y muestra el servicio `cafe-jaen`. Pulsar **Deploy Blueprint**.
4. Esperar el primer build (5–8 min). Cuando diga **Live**, abrir la URL que aparece arriba.
5. Registrarse con un código `DEMO-0001` … `DEMO-0010` (cada código sirve una vez).

### Cosas a saber del plan gratuito

- **Se duerme** tras unos 15 minutos sin visitas; la primera visita después tarda alrededor de
  1 minuto en despertar. Antes de una presentación, abrir la URL 2–3 minutos antes.
- **Los datos se reinician** en cada despliegue o al despertar (SQLite dentro del contenedor).
  Al arrancar se vuelven a cargar los datos y los 10 códigos; las cuentas creadas se pierden.
  Para datos permanentes: crear una base PostgreSQL gratuita (por ejemplo en Neon) y poner su URL
  en la variable `DATABASE_URL` del servicio (formato `postgresql+psycopg2://…`).
- **Precios reales** en lugar del sintético: en *Environment* cambiar `QUOTATION_SOURCES` a
  `["yahoo","stooq"]`, `MARKET_OPENS` a `04:15`, `MARKET_CLOSES` a `13:30` y `DEMO_DATA` a `false`
  (requiere cargar el histórico real; ver `docs/operacion.md`).

### Actualizar la app publicada

```
git add .
git commit -m "feat(...): descripción"
git push
```

Render detecta el push y despliega solo (pestaña **Events** del servicio). Si el build falla,
la versión anterior sigue en línea.

## 2. GitHub Codespaces: editar en tiempo real

1. En GitHub, en el repositorio: **Code** → pestaña **Codespaces** → **Create codespace on main**.
2. Se abre VS Code en el navegador. La primera vez instala todo solo (`.devcontainer/`), unos
   5 minutos: espera a que la terminal termine `python dev.py setup` y `python dev.py demo`.
3. En la terminal: `python dev.py start`. Se abre la app en otra pestaña (puerto 5173).
4. Editar, por ejemplo, `frontend/src/shared/texts/es.ts` o `frontend/src/shared/styles.css` y
   guardar: la app se actualiza al instante sin recargar.
5. Para mostrarla a otra persona: pestaña **Ports** → clic derecho en 5173 → **Port Visibility** →
   **Public**, y compartir esa URL mientras el codespace esté abierto.
6. Al terminar: **Code** → **Codespaces** → detener el codespace para no gastar horas.

Los cambios hechos en el codespace se guardan en el repositorio con `git add`, `git commit` y
`git push`, igual que en local; si Render está conectado, ese push también actualiza la app pública.
