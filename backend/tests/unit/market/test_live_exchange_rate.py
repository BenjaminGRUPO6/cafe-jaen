"""Dólar en vivo (USD/PEN) cada minuto, con el BCRP como respaldo."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from market.domain.errors import SourceUnavailableError
from market.domain.exchange_rate_choice import current_rate, rate_at
from market.domain.quotation import ExchangeRate
from market.infrastructure.sources.live_exchange_rate_sources import (
    build_exchange_sources,
    build_rate,
    parse_tradingview_rate,
)

LIMA = ZoneInfo("America/Lima")
NOW = datetime(2026, 11, 5, 9, 40, tzinfo=LIMA)
BCRP = ExchangeRate(Decimal("3.378"), date(2026, 11, 5), "BCRP")


def live(value: str, at: datetime) -> ExchangeRate:
    return ExchangeRate(Decimal(value), at.date(), "Yahoo Finance (USD/PEN)", rated_at=at)


def test_uses_todays_live_dollar_and_falls_back_to_the_bcrp() -> None:
    today = live("3.381", NOW)
    assert current_rate(today, BCRP, NOW.date(), LIMA) == today
    yesterday = live("3.370", NOW - timedelta(days=1))
    assert current_rate(yesterday, BCRP, NOW.date(), LIMA) == BCRP
    assert current_rate(None, BCRP, NOW.date(), LIMA) == BCRP


def test_each_minute_uses_the_dollar_of_that_moment() -> None:
    rates = [live("3.380", NOW - timedelta(minutes=10)), live("3.384", NOW - timedelta(minutes=2))]
    assert rate_at(NOW - timedelta(minutes=5), rates, BCRP) == rates[0]
    assert rate_at(NOW, rates, BCRP) == rates[1]
    assert rate_at(NOW - timedelta(minutes=30), rates, BCRP) == BCRP  # aún no había dólar en vivo


def test_rejects_an_implausible_dollar() -> None:
    with pytest.raises(SourceUnavailableError):
        build_rate(Decimal("33.8"), NOW, "Web")
    assert build_rate(Decimal("3.38"), NOW, "Web").rated_on == NOW.date()


def test_reads_the_tradingview_forex_scan() -> None:
    payload = {"data": [{"s": "FX_IDC:USDPEN", "d": [3.3815]}]}
    rate = parse_tradingview_rate(payload, "FX_IDC:USDPEN", "TradingView (USD/PEN)")
    assert rate.soles_per_dollar == Decimal("3.3815")
    assert rate.rated_at is not None
    with pytest.raises(SourceUnavailableError):
        parse_tradingview_rate({"data": []}, "FX_IDC:USDPEN", "TradingView (USD/PEN)")


def test_unknown_dollar_sources_are_ignored() -> None:
    names = [s.name for s in build_exchange_sources(["demo", "tradingview"])]
    assert names == ["TradingView (USD/PEN)"]
    assert len(build_exchange_sources([])) == 2
