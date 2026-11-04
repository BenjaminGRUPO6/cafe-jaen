# Atajos opcionales para macOS/Linux. Las tareas principales viven en dev.py (también en Windows).
PY := backend/.venv/bin/python
RUN := cd backend && PYTHONPATH=src .venv/bin/python

.PHONY: setup demo start start-real test check admin reset cycle live backtest codes spike load

setup:  ## Instala todo (igual que: python dev.py setup)
	python3 dev.py setup

demo:  ## Datos de demostración (igual que: python dev.py demo)
	python3 dev.py demo

start:  ## API y app juntas en modo demostración (igual que: python dev.py start)
	python3 dev.py start

start-real:  ## API y app con precios reales de Yahoo y Stooq
	python3 dev.py start --real

test:  ## Pruebas del backend y del frontend
	python3 dev.py test

check:  ## Todo lo que revisa la integración continua
	python3 dev.py check

admin:  ## Cuenta del equipo: make admin PHONE=9XXXXXXXX
	python3 dev.py admin $(PHONE)

reset:  ## Borra la base de datos local
	python3 dev.py reset

# ---- Tareas de operación e investigación ----
cycle:  ## Ciclo de cierre una vez: cierre del día, histórico y pronóstico
	$(RUN) scripts/run_daily_cycle.py

live:  ## Recolección en vivo una vez (lo que el planificador hace cada minuto)
	$(RUN) scripts/run_daily_cycle.py --live

backtest:  ## Prueba retrospectiva de «¿Vendo ahora o espero?» con varios umbrales (T30)
	$(RUN) scripts/backtest_selling_rule.py --days 250 --thresholds 0.01 0.02 0.03

codes:  ## Genera 30 códigos de invitación para el grupo experimental (GE-01 … GE-30)
	$(RUN) scripts/create_invitation_codes.py --count 30

spike:  ## Compara las webs del precio durante 60 min con la bolsa abierta (T01)
	$(RUN) scripts/spike_sources.py --minutes 60

load:  ## Prueba de carga: 30 usuarios por 60 s (requiere `python dev.py start` corriendo)
	$(RUN) scripts/create_load_test_codes.py
	cd backend && .venv/bin/locust -f tests/load/locustfile.py --headless -u 30 -r 10 -t 60s --host http://localhost:8000
