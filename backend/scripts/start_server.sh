#!/bin/sh
# Arranque en producción (Render): migraciones → cuenta del equipo → datos demo (opcional) → API.
set -e
alembic upgrade head
# Cuenta del equipo desde ADMIN_PHONE y ADMIN_PASSWORD (idempotente; si faltan, no hace nada)
python scripts/ensure_admin.py
if [ "$DEMO_DATA" = "true" ]; then
  # Idempotente: si los datos ya existen, no los duplica
  python scripts/seed_demo_data.py
  python scripts/run_daily_cycle.py
fi
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir src --proxy-headers --forwarded-allow-ips="*"
