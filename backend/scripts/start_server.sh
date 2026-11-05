#!/bin/sh
# Arranque en producción (Render): migraciones → datos de demostración (opcional) → API.
set -e
alembic upgrade head
if [ "$DEMO_DATA" = "true" ]; then
  # Idempotente: si los datos ya existen, no los duplica
  python scripts/seed_demo_data.py
  python scripts/run_daily_cycle.py
fi
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --app-dir src --proxy-headers --forwarded-allow-ips="*"
