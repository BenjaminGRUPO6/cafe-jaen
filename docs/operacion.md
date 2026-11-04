# Operación

## Primer despliegue

1. Crear la base de datos PostgreSQL y definir `DATABASE_URL`, `JWT_SECRET` (largo y aleatorio).
2. `alembic upgrade head` (lo hace el contenedor al iniciar).
3. Cargar el histórico real (5 años de cierres diarios y tipo de cambio):
   `PYTHONPATH=src python scripts/load_price_history.py --years 5`
4. Generar el primer pronóstico: `PYTHONPATH=src python scripts/run_daily_cycle.py`
5. Medir el acierto de la regla de venta y configurarlo en `SELLING_HIT_RATE_PCT`:
   `PYTHONPATH=src python scripts/backtest_selling_rule.py --days 250 --thresholds 0.01 0.02 0.03`
6. Crear las cuentas del equipo (pueden anotar precios de cooperativas):
   `PYTHONPATH=src python scripts/create_admin.py --phone 9XXXXXXXX` (pide la contraseña).
7. Generar los códigos del grupo experimental:
   `PYTHONPATH=src python scripts/create_invitation_codes.py --count 30`
   y entregarlos en sobre cerrado. Los participantes del grupo de control **no** reciben código.
8. Publicar el front-end (`npm run build` → carpeta `dist/`) con `VITE_API_URL` apuntando a la API.

## Fuentes de datos (verificar en la Iteración 0 con `make spike`)

| Dato | Fuente | Dónde se configura |
|---|---|---|
| Precio de la bolsa de Nueva York (café arábica, contrato C) | Yahoo Finance (`KC=F`, minuto a minuto vía yfinance) | `market/infrastructure/sources/yahoo_quotation_source.py` |
| Mismo precio, segunda web | Stooq (CSV público, `KC.F`; hora de Polonia, `STOOQ_TIMEZONE`) | `market/infrastructure/sources/stooq_quotation_source.py` |
| Tipo de cambio | API del BCRP, serie `PD04640PD` (una vez al día) | `market/infrastructure/sources/bcrp_exchange_rate_provider.py` |

- Las webs a usar se eligen con `QUOTATION_SOURCES` (por defecto `["yahoo","stooq"]`).
- **Agregar una tercera web** = crear un adaptador que implemente `QuotationSource`
  (`name` y `fetch_latest()`), registrarlo en `_quotation_sources()` de `main.py` y añadir su
  prueba de lectura (como `test_source_parsers.py`).
- El formato de Stooq y su zona horaria se escribieron según su CSV público y **deben
  confirmarse con el spike** desde el servidor de producción, junto con los términos de uso de
  cada web. Si una web cambia, solo se reemplaza su adaptador.
- Datos segundo a segundo de ICE requieren licencia: queda como mejora futura.

## Sin internet (desarrollo y demostraciones)

`python dev.py demo` carga datos SINTÉTICOS (incluidos precios de cooperativas de ejemplo) y
`python dev.py start` levanta la API con la fuente `demo` y la bolsa «abierta» todo el día, junto
con la app, para ver el precio moverse en vivo. **Nunca** usar en el experimento: allí se usa
`DATABASE_URL` de PostgreSQL y las fuentes reales (`python dev.py start --real` o el despliegue
con Docker).

## Durante el experimento

- **Precios de cooperativas (HU12):** cada día hábil, quien esté de turno llama a 2–3
  cooperativas y anota su precio en «Equipo». El estimado usa los últimos 30 días; con menos de
  3 precios de un tipo de café la app avisa «pocos datos».

- La versión **v1.1 queda congelada** para el experimento: solo correcciones por rama `hotfix/`.
- Entregar un código de invitación por participante del GE (`make codes`), anotando a quién se entrega (GE-01 a GE-30).
- Revisar cada semana los incidentes de recolección (logs): webs caídas, webs descartadas por
  discrepar y precios marcados como desactualizados; y la tabla `agent_traces`.
- La tabla `live_quotes` crece unas 550 filas por día hábil: no requiere limpieza durante el
  experimento.
- Respaldo diario de la base de datos (`pg_dump`) y prueba de restauración mensual.

## Asesor con LLM real (opcional)

`LLM_PROVIDER=anthropic` y `ANTHROPIC_API_KEY=...`. Sin clave, el asesor usa el modelo por
palabras clave, que funciona sin internet y sin costo.
