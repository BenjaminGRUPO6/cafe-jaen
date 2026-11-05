# Despliegue y edición en línea

Para mostrar el software sin depender de una computadora local, lo publicamos de dos formas
gratuitas:

| Opción | Para qué la usamos | Costo |
|---|---|---|
| **Render** | App pública con una URL fija (`https://cafe-jaen.onrender.com`). Cada `git push` a `main` la vuelve a desplegar. | Gratis (plan *Free*) |
| **GitHub Codespaces** | El proyecto completo en el navegador: editamos el código y vemos el cambio en la app al instante. | Gratis (horas mensuales incluidas en la cuenta de GitHub) |

## 1. Render: app pública

### Cómo lo armamos

```
GitHub (main) ──push──► Render construye el Dockerfile de la raíz
                         ├─ etapa 1: node 22 compila el front-end (PWA)
                         └─ etapa 2: python 3.12 + API FastAPI que también entrega la app
                                    └─ scripts/start_server.sh
                                       migraciones → datos demo → uvicorn
```

- **Un solo servicio y una sola URL:** la API (`/api/...`) y la app comparten dominio, así que no
  necesitamos CORS. La API entrega la app compilada cuando se define `STATIC_DIR`
  (`backend/src/shared/infrastructure/api/spa.py`).
- **Infraestructura como código:** `render.yaml` (Blueprint) declara el servicio y sus variables;
  el `JWT_SECRET` lo genera Render.
- **Modo demostración:** precio sintético que se mueve todo el día y códigos **DEMO-0001 a
  DEMO-0010**. El script de datos es idempotente: si los datos ya existen, no los duplica.

### Cómo lo publicamos

1. Iniciamos sesión en <https://render.com> con la cuenta de GitHub dueña del repositorio.
2. **New +** → **Blueprint** → elegimos el repositorio y le damos acceso a la GitHub App de Render.
3. Render leyó `render.yaml` y propuso el servicio `cafe-jaen`; lo creamos con **Deploy Blueprint**.
4. El primer build tardó unos minutos. En los *Logs* se ve el arranque:

   ```
   Datos de demostración cargados. Códigos de invitación: DEMO-0001 a DEMO-0010
   Pronóstico generado: True
   Uvicorn running on http://0.0.0.0:10000
   ==> Your service is live
   ```

5. Con el servicio en **Live**, abrimos la URL y nos registramos con un código `DEMO-0001` …
   `DEMO-0010` (cada código sirve una vez).

### Limitaciones del plan gratuito

- **Se duerme** tras unos 15 minutos sin visitas; la primera visita después tarda alrededor de
  1 minuto en despertar. Antes de una presentación, abrimos la URL 2–3 minutos antes.
- **Los datos se reinician** en cada despliegue o al despertar, porque SQLite vive dentro del
  contenedor. Al arrancar se vuelven a cargar los datos y los 10 códigos, pero las cuentas creadas
  se pierden. Para datos permanentes basta con una base PostgreSQL gratuita (por ejemplo, Neon)
  en la variable `DATABASE_URL` (formato `postgresql+psycopg2://…`).
- **Precios reales** en lugar del sintético: en *Environment* se cambia `QUOTATION_SOURCES` a
  `["yahoo","stooq"]`, `MARKET_OPENS` a `04:15`, `MARKET_CLOSES` a `13:30` y `DEMO_DATA` a `false`
  (requiere cargar el histórico real; ver `docs/operacion.md`).

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
   `python dev.py demo`), en unos 5 minutos.
3. En la terminal: `python dev.py start`. La app se abre en otra pestaña (puerto 5173).
4. Al editar, por ejemplo, `frontend/src/shared/texts/es.ts` o `frontend/src/shared/styles.css` y
   guardar, la app se actualiza al instante sin recargar.
5. Para mostrarla a otra persona: pestaña **Ports** → clic derecho en 5173 → **Port Visibility** →
   **Public**, y se comparte esa URL mientras el codespace esté abierto.
6. Al terminar: **Code** → **Codespaces** → detener el codespace para no gastar horas.

Los cambios hechos en el codespace se guardan con `git add`, `git commit` y `git push`, igual que
en local; ese push también actualiza la app publicada en Render.
