"""Registro de cada consulta: qué marcó cada web y por qué se publicó ese precio."""

from datetime import timedelta
from decimal import Decimal

from market.application.collect_prices import CollectPrices
from market.application.get_price_log import GetPriceLog
from market.domain.consensus import Consensus
from market.domain.errors import SourceUnavailableError
from market.domain.local_price import LocalPriceEstimator
from market.domain.market_hours import MarketHours
from market.domain.price_validator import PriceValidator
from market.domain.quintal_price import PriceConverter
from market.domain.source_reading import CollectionOutcome, ReadingStatus
from tests.fakes import (
    FakeProvider,
    FixedClock,
    InMemoryPriceRepository,
    live,
    rate,
    source,
)

CLOCK = FixedClock()
NOW = CLOCK.now()


def collect(prices: InMemoryPriceRepository, *sources: object) -> None:
    CollectPrices(
        list(sources),  # type: ignore[arg-type]
        FakeProvider(rate("3.75", CLOCK.today())),
        prices,
        Consensus(),
        PriceValidator(),
        MarketHours(),
        CLOCK,
    ).execute(force=True)


def test_records_used_discarded_and_failed_sources() -> None:
    prices = InMemoryPriceRepository()
    moment = NOW - timedelta(minutes=2)

    collect(
        prices,
        source("Yahoo Finance", live("300", moment)),
        source("Stooq", live("301", moment)),
        source("Otra web", live("320", moment)),  # 6 % lejos de la mediana: se descarta
        source("Web caída", SourceUnavailableError("sin conexión")),
    )

    (collection,) = prices.collections
    by_source = {r.source: r for r in collection.readings}
    assert by_source["Yahoo Finance"].status is ReadingStatus.USED
    assert by_source["Stooq"].status is ReadingStatus.USED
    assert by_source["Otra web"].status is ReadingStatus.DISCARDED
    assert by_source["Otra web"].deviation_pct == Decimal("6.31")
    assert by_source["Web caída"].status is ReadingStatus.FAILED
    assert by_source["Web caída"].detail
    assert collection.median_cents == Decimal("301")
    assert collection.published_cents == Decimal("300.5000")


def test_a_collection_without_agreement_is_recorded_but_not_published() -> None:
    prices = InMemoryPriceRepository()
    moment = NOW - timedelta(minutes=2)

    collect(prices, source("A", live("300", moment)), source("B", live("330", moment)))

    (collection,) = prices.collections
    assert not collection.published
    assert prices.live == []
    entries = GetPriceLog(prices, PriceConverter(), LocalPriceEstimator(), CLOCK).execute().entries
    assert len(entries) == 1
    assert not entries[0].published
    assert entries[0].price_soles is None
    assert {r.status for r in entries[0].readings} == {ReadingStatus.DISCARDED}


def test_price_log_attaches_readings_to_the_published_quote() -> None:
    prices = InMemoryPriceRepository()
    moment = NOW - timedelta(minutes=2)

    collect(
        prices, source("Yahoo Finance", live("300", moment)), source("Stooq", live("300", moment))
    )

    entries = GetPriceLog(prices, PriceConverter(), LocalPriceEstimator(), CLOCK).execute().entries
    assert len(entries) == 1  # la cotización publicada no se repite como fila aparte
    assert entries[0].sources == ("Yahoo Finance", "Stooq")
    assert len(entries[0].readings) == 2


def test_a_repeated_quote_is_recorded_as_unchanged_not_as_rejected() -> None:
    prices = InMemoryPriceRepository()
    moment = NOW - timedelta(minutes=25)
    collect(prices, source("Yahoo Finance", live("280.80", moment)))
    collect(prices, source("Yahoo Finance", live("280.80", moment)))  # la web repite la misma

    first, second = prices.collections
    assert first.outcome is CollectionOutcome.PUBLISHED
    assert second.outcome is CollectionOutcome.UNCHANGED
    assert second.detail


def test_nothing_answered_is_recorded_as_no_data() -> None:
    prices = InMemoryPriceRepository()

    collect(prices, source("Stooq", SourceUnavailableError("timed out")))

    (collection,) = prices.collections
    assert collection.outcome is CollectionOutcome.NO_DATA
