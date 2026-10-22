"""Prueba retrospectiva de «¿Vendo ahora o espero?» (T30, HU05).

Para cada día del periodo evaluado: se pronostica con los datos que había HASTA ese día
(mismo criterio de elección de modelo que el Agente Predictor), se aplica la regla y se
compara con lo que realmente pasó en los 7 días hábiles siguientes.
El porcentaje de acierto se configura luego en SELLING_HIT_RATE_PCT para mostrarlo en la app.

Uso:  python scripts/backtest_selling_rule.py --days 250 --thresholds 0.01 0.02 0.03
"""

import argparse
from datetime import date
from decimal import Decimal

from decision.domain.backtest import BacktestResult
from decision.domain.selling_decision import ForecastDay, MarketSnapshot, SellingDecision, Verdict
from forecasting.domain.forecast import Forecast
from forecasting.domain.metrics import mean_absolute_percentage_error
from forecasting.infrastructure.models.elm_forecast_model import ElmForecastModel
from forecasting.infrastructure.models.naive_forecast_model import NaiveDriftForecastModel
from market.application.get_price_history import GetPriceHistory
from market.domain.quintal_price import PriceConverter
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock

HORIZON, VALIDATION_DAYS, MIN_TRAINING = 7, 30, 250


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=250, help="días hábiles a evaluar")
    parser.add_argument("--thresholds", type=Decimal, nargs="+", default=None)
    args = parser.parse_args()

    settings = get_settings()
    repository = SqlAlchemyPriceRepository(
        create_session_factory(create_db_engine(settings.database_url))
    )
    history = GetPriceHistory(
        repository, PriceConverter(settings.local_price_factor), SystemClock()
    )
    points = history.daily(settings.forecast_history_days)
    series = [float(p.price.soles) for p in points]
    days = [p.priced_on for p in points]
    first = max(MIN_TRAINING, len(series) - HORIZON - args.days)
    if first >= len(series) - HORIZON:
        raise SystemExit(f"No hay suficiente histórico: {len(series)} días")

    # Los pronósticos se calculan una sola vez y se prueban con cada umbral
    models = [ElmForecastModel(), NaiveDriftForecastModel()]
    cases = []
    for t in range(first, len(series) - HORIZON):
        forecast = _forecast(models, series[: t + 1], days[t], days[t + 1 : t + 1 + HORIZON])
        snapshot = MarketSnapshot(
            current_price=Decimal(str(series[t])),
            priced_at=days[t].isoformat(),
            price_is_stale=False,
            forecast=[ForecastDay(p.day, p.expected, p.lower, p.upper) for p in forecast.points],
            forecast_generated_on=days[t],
        )
        future = [Decimal(str(v)) for v in series[t + 1 : t + 1 + HORIZON]]
        cases.append((days[t], snapshot, future))

    print(f"Días evaluados: {len(cases)} (del {cases[0][0]} al {cases[-1][0]})")
    for threshold in args.thresholds or [settings.selling_threshold]:
        rule, result = SellingDecision(threshold), BacktestResult()
        for day, snapshot, future in cases:
            result.add(rule.decide(snapshot, day).verdict, snapshot.current_price, future)
        print(f"\nUmbral {threshold * 100:.1f} %")
        for verdict in Verdict:
            if result.counts[verdict]:
                scored = verdict in (Verdict.WAIT, Verdict.SELL_NOW)
                detail = f"aciertos {result.hits[verdict]}" if scored else "no se califica"
                print(f"  {verdict.value:<22} {result.counts[verdict]:>4} veces, {detail}")
        print(f"  Acierto de la regla (Esperar + Vender ahora): {result.hit_rate_pct} %")
        print(f"  Referencia «vender siempre de inmediato»:     {result.always_sell_rate_pct} %")


def _forecast(models: list, past: list[float], today: date, next_days: list[date]) -> Forecast:  # type: ignore[type-arg]
    training, actual = past[:-VALIDATION_DAYS], past[-VALIDATION_DAYS:]
    scored = [
        (mean_absolute_percentage_error(actual, m.predict(training, len(actual))), m)
        for m in models
    ]
    mape, best = min(scored, key=lambda score: score[0])
    return Forecast.from_predictions(today, best.name, mape, next_days, best.predict(past, HORIZON))


if __name__ == "__main__":
    main()
