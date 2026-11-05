#!/bin/sh
# Arranque en producción (Render): migraciones → cuenta del equipo → API.
# Datos reales: cuatro webs de la bolsa de Nueva York y el BCRP (tipo de cambio).
set -e
alembic upgrade head
# Cuenta del equipo desde ADMIN_PHONE y ADMIN_PASSWORD (idempotente; si faltan, no hace nada)
python scripts/ensure_admin.py

# Tareas que consultan webs externas: van en segundo plano y con tiempo máximo, porque Render
# cancela el despliegue si la app no abre su puerto en 15 minutos (una web lenta lo bloqueaba).
# Si alguna no termina, la API funciona igual y el Recolector sigue cada minuto.
(
  timeout 600 python scripts/load_price_history.py --years 5 \
    || echo "Aviso: el histórico real no terminó de cargarse (se reintenta en el próximo arranque)"
  timeout 300 python scripts/run_daily_cycle.py \
    || echo "Aviso: no se pudo generar el pronóstico todavía (se genera después del cierre)"
  # Demostración (DEMO_COOPERATIVES=true): precios sintéticos de cooperativas sobre la bolsa real
  timeout 120 python scripts/ensure_demo_cooperatives.py \
    || echo "Aviso: no se cargaron los precios sintéticos (la app reintenta cada 5 minutos)"
) &

exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir src --proxy-headers --forwarded-allow-ips="*"
