# Atajos para el día a día. Ejecutar desde la raíz del repositorio.
PY := backend/.venv/bin/python

.PHONY: setup test lint load api api-demo web demo cycle live backtest codes admin spike

setup:  ## Crea el entorno de Python e instala dependencias del backend y front-end
	python3 -m venv backend/.venv
	$(PY) -m pip install -e "backend[dev]"
	cd frontend && npm ci

test:  ## Todas las pruebas (backend y front-end)
	cd backend && .venv/bin/pytest
	cd frontend && npm test

lint:  ## Estilo, tipos y contratos de arquitectura
	cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy && PYTHONPATH=src .venv/bin/lint-imports
	cd frontend && npm run lint

api:  ## API en http://localhost:8000 (documentación en /docs)
	cd backend && .venv/bin/alembic upgrade head && .venv/bin/uvicorn main:app --reload --app-dir src

api-demo:  ## API SIN internet: precio sintético en vivo y bolsa «abierta» todo el día
	cd backend && .venv/bin/alembic upgrade head && QUOTATION_SOURCES='["demo"]' MARKET_OPENS=00:00 MARKET_CLOSES=23:59 .venv/bin/uvicorn main:app --reload --app-dir src

web:  ## Front-end en http://localhost:5173
	cd frontend && npm run dev

demo:  ## Datos SINTÉTICOS para probar sin internet (código DEMO-0001)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/seed_demo_data.py

cycle:  ## Ejecuta una vez el ciclo de cierre: cierre del día, histórico y pronóstico
	cd backend && PYTHONPATH=src .venv/bin/python scripts/run_daily_cycle.py

live:  ## Ejecuta una vez la recolección en vivo (lo que el planificador hace cada minuto)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/run_daily_cycle.py --live

backtest:  ## Prueba retrospectiva de «¿Vendo ahora o espero?» con varios umbrales (T30)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/backtest_selling_rule.py --days 250 --thresholds 0.01 0.02 0.03

codes:  ## Genera 30 códigos de invitación para el grupo experimental
	cd backend && PYTHONPATH=src .venv/bin/python scripts/create_invitation_codes.py --count 30

admin:  ## Crea una cuenta del equipo para anotar precios de cooperativas (make admin PHONE=9XXXXXXXX)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/create_admin.py --phone $(PHONE)

spike:  ## Compara las webs del precio durante 60 min con la bolsa abierta (T01)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/spike_sources.py --minutes 60

load:  ## Prueba de carga: 30 usuarios por 60 s (requiere la API levantada y `make demo`)
	cd backend && PYTHONPATH=src .venv/bin/python scripts/create_load_test_codes.py
	cd backend && .venv/bin/locust -f tests/load/locustfile.py --headless -u 30 -r 10 -t 60s --host http://localhost:8000
