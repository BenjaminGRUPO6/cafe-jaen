#!/bin/sh
# Arranque en producción (Render): migraciones → cuenta del equipo → histórico real → API.
# Datos reales: cuatro webs de la bolsa de Nueva York y el BCRP (tipo de cambio).
set -e
alembic upgrade head
# Cuenta del equipo desde ADMIN_PHONE y ADMIN_PASSWORD (idempotente; si faltan, no hace nada)
python scripts/ensure_admin.py
# Histórico real de 5 años (idempotente). Si las webs no responden, la API arranca igual
# y el Recolector sigue intentando cada minuto con la bolsa abierta.
python scripts/load_price_history.py --years 5 || echo "Aviso: no se pudo cargar el histórico real"
python scripts/run_daily_cycle.py || echo "Aviso: no se pudo generar el pronóstico todavía"
# Demostración (DEMO_COOPERATIVES=true): precios sintéticos de cooperativas sobre la bolsa real
python scripts/ensure_demo_cooperatives.py || echo "Aviso: no se cargaron los precios sintéticos"
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir src --proxy-headers --forwarded-allow-ips="*"
