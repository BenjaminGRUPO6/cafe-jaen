"""TradingView se consulta cada 5 minutos y, si responde 429, se pausa."""

from datetime import UTC, datetime, timedelta

import pytest

from market.domain.errors import RateLimitedError, SourcePausedError
from market.infrastructure.sources.throttled_source import ThrottledSource
from tests.fakes import FakeProvider, live


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 5, 15, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


def test_queries_at_most_once_per_interval() -> None:
    clock = Clock()
    quote = live("277", clock.now)
    web = ThrottledSource(
        FakeProvider(quote, quote, name="TradingView"), timedelta(minutes=5), clock
    )

    assert web.fetch_latest() == quote
    clock.now += timedelta(minutes=1)
    with pytest.raises(SourcePausedError, match="4 min"):
        web.fetch_latest()
    clock.now += timedelta(minutes=4)
    assert web.fetch_latest() == quote


def test_a_429_pauses_the_web_for_the_time_it_asks() -> None:
    clock = Clock()
    quote = live("277", clock.now)
    limited = RateLimitedError("pidió esperar", retry_after_seconds=600)
    web = ThrottledSource(
        FakeProvider(limited, quote, name="TradingView"), timedelta(minutes=5), clock
    )

    with pytest.raises(RateLimitedError):
        web.fetch_latest()
    clock.now += timedelta(minutes=9)
    with pytest.raises(SourcePausedError):
        web.fetch_latest()
    clock.now += timedelta(minutes=1)
    assert web.fetch_latest() == quote
