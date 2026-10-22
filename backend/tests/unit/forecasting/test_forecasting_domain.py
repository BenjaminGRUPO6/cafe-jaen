from datetime import date
from decimal import Decimal

import pytest

from forecasting.domain.business_days import next_business_days
from forecasting.domain.forecast import Forecast
from forecasting.domain.metrics import mean_absolute_percentage_error


def test_mape_is_average_percentage_error() -> None:
    assert mean_absolute_percentage_error([100, 200], [110, 180]) == pytest.approx(10.0)


def test_mape_requires_same_length() -> None:
    with pytest.raises(ValueError):
        mean_absolute_percentage_error([1, 2], [1])


def test_next_business_days_skip_weekend() -> None:
    friday = date(2026, 11, 6)

    assert next_business_days(friday, 2) == [date(2026, 11, 9), date(2026, 11, 10)]


def test_forecast_range_is_expected_plus_minus_mape() -> None:
    forecast = Forecast.from_predictions(
        date(2026, 11, 4), "elm", 5.0, [date(2026, 11, 5)], [1000.0]
    )

    point = forecast.points[0]
    assert (point.lower, point.expected, point.upper) == (
        Decimal("950.00"),
        Decimal("1000.00"),
        Decimal("1050.00"),
    )
