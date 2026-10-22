"""PA-05-1 a PA-05-4 (HU05): regla «¿Vendo ahora o espero?» y su prueba retrospectiva."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from decision.domain.backtest import BacktestResult, was_right
from decision.domain.selling_decision import (
    ForecastDay,
    MarketSnapshot,
    SellingDecision,
    Verdict,
)

TODAY = date(2026, 11, 4)


def forecast(*values: tuple[str, str, str]) -> list[ForecastDay]:
    return [
        ForecastDay(TODAY + timedelta(days=i + 1), Decimal(e), Decimal(lo), Decimal(up))
        for i, (e, lo, up) in enumerate(values)
    ]


def snapshot(points: list[ForecastDay], stale: bool = False, age_days: int = 0) -> MarketSnapshot:
    return MarketSnapshot(
        current_price=Decimal("1140"),
        priced_at="2026-11-04T09:00:00-05:00",
        price_is_stale=stale,
        forecast=points,
        forecast_generated_on=TODAY - timedelta(days=age_days),
    )


def test_waits_when_forecast_rises_and_range_stays_above_today() -> None:
    advice = SellingDecision().decide(snapshot(forecast(("1190", "1150", "1230"))), TODAY)

    assert advice.verdict is Verdict.WAIT
    assert advice.change_pct == Decimal("4.4")
    assert "S/ 1140,00 a S/ 1190,00" in advice.reason


def test_does_not_wait_if_worst_case_is_below_today() -> None:
    advice = SellingDecision().decide(snapshot(forecast(("1190", "1100", "1280"))), TODAY)

    assert advice.verdict is Verdict.NO_SIGNAL


def test_sells_now_when_forecast_falls_more_than_threshold() -> None:
    advice = SellingDecision().decide(
        snapshot(forecast(("1120", "1080", "1160"), ("1090", "1050", "1130"))), TODAY
    )

    assert advice.verdict is Verdict.SELL_NOW
    assert advice.target_price == Decimal("1090")
    assert "conviene vender ahora" in advice.reason


def test_small_change_gives_no_clear_signal() -> None:
    advice = SellingDecision().decide(snapshot(forecast(("1150", "1120", "1180"))), TODAY)

    assert advice.verdict is Verdict.NO_SIGNAL
    assert "3,0 %" in advice.reason


@pytest.mark.parametrize(
    "case",
    [
        snapshot(forecast(("1190", "1150", "1230")), stale=True),
        snapshot([]),
        snapshot(forecast(("1190", "1150", "1230")), age_days=6),
    ],
)
def test_does_not_recommend_without_fresh_data(case: MarketSnapshot) -> None:
    advice = SellingDecision().decide(case, TODAY)

    assert advice.verdict is Verdict.NO_DATA and advice.current_price is None


@pytest.mark.parametrize(
    ("verdict", "future", "expected"),
    [
        (Verdict.WAIT, ["1150"], True),
        (Verdict.WAIT, ["1130"], False),
        (Verdict.SELL_NOW, ["1160", "1140"], True),  # cuenta el precio al final del horizonte
        (Verdict.SELL_NOW, ["1141"], False),
        (Verdict.NO_SIGNAL, ["1200"], None),
        (Verdict.WAIT, [], None),
    ],
)
def test_backtest_scores_each_recommendation(
    verdict: Verdict, future: list[str], expected: bool | None
) -> None:
    assert was_right(verdict, Decimal("1140"), [Decimal(v) for v in future]) is expected


def test_backtest_result_counts_hits_and_baseline() -> None:
    result = BacktestResult()
    result.add(Verdict.WAIT, Decimal("100"), [Decimal("101")])  # acierto
    result.add(Verdict.SELL_NOW, Decimal("100"), [Decimal("105")])  # fallo
    result.add(Verdict.NO_SIGNAL, Decimal("100"), [Decimal("99")])  # no se califica

    assert result.scored == 2 and result.hit_rate_pct == 50.0
    assert result.always_sell_rate_pct == 33.3  # solo el último día el precio final no fue mayor
