"""Ejecuta una vez el ciclo autónomo (cierre → histórico → pronóstico).

Con --live ejecuta solo una recolección en vivo (lo que el planificador hace cada minuto).
Útil para la demostración y para generar el primer pronóstico tras la carga inicial.
"""

import argparse

from main import create_app
from shared.infrastructure.settings import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="solo una recolección en vivo")
    app = create_app(Settings(scheduler_enabled=False))
    if parser.parse_args().live:
        print(f"Recolección en vivo: {app.state.live_collection.execute()}")
        return
    report = app.state.daily_cycle.execute()
    print(f"Recolección: {report.collection}")
    print(f"Pronóstico generado: {report.forecast_generated} {report.detail or ''}")


if __name__ == "__main__":
    main()
