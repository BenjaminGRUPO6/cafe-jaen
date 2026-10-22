"""PA-03-1 a PA-03-3 (HU03) y HU04: precio en vivo, variación e histórico."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from market.application.get_live_price import GetLivePrice
from market.application.get_price_history import GetPriceHistory
from market.domain.errors import PriceNotAvailableError
from market.domain.market_hours import MarketHours
from market.domain.quintal_price import PriceConverter
from tests.fakes import LIMA, FixedClock, InMemoryPriceRepository, live, quotation, rate

CLOCK = FixedClock(datetime(2026, 11, 4, 9, 0, tzinfo=LIMA))


def live_price(repository: InMemoryPriceRepository, clock: FixedClock = CLOCK) -> GetLivePrice:
    return GetLivePrice(repository, PriceConverter(), MarketHours(), clock)


@pytest.fixture
def repository() -> InMemoryPriceRepository:
    repo = InMemoryPriceRepository()
    repo.add_exchange_rate(rate("3.75", date(2026, 11, 2)))
    repo.save_daily_close(quotation("289.246", date(2026, 11, 3)))  # = S/ 1100,00
    repo.add_live_quote(live("300", datetime(2026, 11, 4, 8, 55, tzinfo=LIMA)))  # = S/ 1140,89
    return repo


def test_live_price_includes_change_against_previous_close(
    repository: InMemoryPriceRepository,
) -> None:
    price = live_price(repository).execute()

    assert price.cents_per_pound == Decimal("300")
    assert price.price.soles == Decimal("1140.89")
    assert price.previous_close is not None and price.previous_close.soles == Decimal("1100.00")
    assert price.change_soles == Decimal("40.89")
    assert price.change_pct == Decimal("3.72")
    assert price.sources == ("Yahoo Finance", "BCRP")
    assert price.market_open and not price.stale


def test_old_price_with_market_open_is_marked_stale(repository: InMemoryPriceRepository) -> None:
    later = FixedClock(CLOCK.current + timedelta(minutes=40))

    assert live_price(repository, later).execute().stale


def test_without_live_quotes_uses_last_daily_close() -> None:
    repo = InMemoryPriceRepository()
    repo.add_exchange_rate(rate("3.75", date(2026, 11, 2)))
    repo.save_daily_close(quotation("300", date(2026, 11, 3)))

    price = live_price(repo).execute()

    assert price.price.soles == Decimal("1140.89")
    assert price.quoted_at.date() == date(2026, 11, 3)


def test_live_price_without_data_fails_clearly() -> None:
    with pytest.raises(PriceNotAvailableError):
        live_price(InMemoryPriceRepository()).execute()


def test_daily_history_uses_rate_in_force_each_day(repository: InMemoryPriceRepository) -> None:
    repository.save_daily_close(quotation("300", date(2026, 11, 4)))
    repository.add_exchange_rate(rate("3.80", date(2026, 11, 4)))

    points = GetPriceHistory(repository, PriceConverter(), CLOCK).daily(days=30)

    assert [p.priced_on for p in points] == [date(2026, 11, 3), date(2026, 11, 4)]
    assert points[0].price.soles == Decimal("1100.00")  # usa el TC del 02/11
    assert points[1].price.soles == Decimal("1156.10")  # usa el TC del 04/11


def test_intraday_history_returns_today_minute_by_minute(
    repository: InMemoryPriceRepository,
) -> None:
    repository.add_live_quote(live("301", datetime(2026, 11, 4, 8, 56, tzinfo=LIMA)))
    repository.add_live_quote(live("280", datetime(2026, 11, 3, 12, 0, tzinfo=LIMA)))  # ayer

    points = GetPriceHistory(repository, PriceConverter(), CLOCK).intraday()

    assert [p.quoted_at.minute for p in points] == [55, 56]


def test_intraday_history_is_empty_without_live_quotes() -> None:
    assert GetPriceHistory(InMemoryPriceRepository(), PriceConverter(), CLOCK).intraday() == []
