"""Compara los modelos de pronóstico con el histórico real (T17, PA-06-1).

Imprime el MAPE de cada modelo para varios horizontes de validación. La tabla resultante
es insumo del capítulo de resultados de la tesis.
Uso:  python scripts/evaluate_forecast_models.py --days 1825
"""

import argparse

from forecasting.domain.metrics import mean_absolute_percentage_error
from forecasting.infrastructure.models.elm_forecast_model import ElmForecastModel
from forecasting.infrastructure.models.naive_forecast_model import NaiveDriftForecastModel
from market.application.get_price_history import GetPriceHistory
from market.domain.quintal_price import PriceConverter
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock

VALIDATION_WINDOWS = [7, 15, 30]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=1825)
    days = parser.parse_args().days

    settings = get_settings()
    repository = SqlAlchemyPriceRepository(
        create_session_factory(create_db_engine(settings.database_url))
    )
    history = GetPriceHistory(
        repository, PriceConverter(settings.local_price_factor), SystemClock()
    )
    series = [float(point.price.soles) for point in history.daily(days)]
    print(f"Precios disponibles: {len(series)}\n")

    print(f"{'Modelo':<14}" + "".join(f"MAPE {w:>2} días  " for w in VALIDATION_WINDOWS))
    for model in (ElmForecastModel(), NaiveDriftForecastModel()):
        scores = []
        for window in VALIDATION_WINDOWS:
            predicted = model.predict(series[:-window], window)
            scores.append(mean_absolute_percentage_error(series[-window:], predicted))
        print(f"{model.name:<14}" + "".join(f"{score:>10.2f} %   " for score in scores))


if __name__ == "__main__":
    main()
