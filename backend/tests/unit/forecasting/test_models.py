import math

import pytest

from forecasting.domain.metrics import mean_absolute_percentage_error
from forecasting.infrastructure.models.elm_forecast_model import ElmForecastModel
from forecasting.infrastructure.models.naive_forecast_model import NaiveDriftForecastModel


def seasonal_series(length: int) -> list[float]:
    return [1100 + 80 * math.sin(i / 6) for i in range(length)]


def test_naive_drift_continues_the_trend() -> None:
    assert NaiveDriftForecastModel().predict([100, 110, 120], 2) == [130, 140]


def test_elm_is_reproducible() -> None:
    history = seasonal_series(200)

    assert ElmForecastModel().predict(history, 7) == ElmForecastModel().predict(history, 7)


def test_elm_learns_a_seasonal_pattern_better_than_naive() -> None:
    series = seasonal_series(230)
    training, actual = series[:200], series[200:]

    elm_error = mean_absolute_percentage_error(actual, ElmForecastModel().predict(training, 30))
    naive_error = mean_absolute_percentage_error(
        actual, NaiveDriftForecastModel().predict(training, 30)
    )

    assert elm_error < naive_error


@pytest.mark.parametrize("horizon", [1, 7])
def test_models_return_one_value_per_day(horizon: int) -> None:
    history = seasonal_series(100)

    assert len(ElmForecastModel().predict(history, horizon)) == horizon
    assert len(NaiveDriftForecastModel().predict(history, horizon)) == horizon
