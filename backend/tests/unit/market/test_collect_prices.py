"""PA-02-1 a PA-02-4 (HU02): varias fuentes, horario de bolsa y último valor válido."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from market.application.collect_prices import CollectPrices
from market.domain.consensus import Consensus
from market.domain.errors import SourceUnavailableError
from market.domain.market_hours import MarketHours
from market.domain.price_validator import PriceValidator
from tests.fakes import (
    LIMA,
    FakeProvider,
    FixedClock,
    InMemoryPriceRepository,
    live,
    rate,
    source,
)

OPEN = FixedClock(datetime(2026, 11, 4, 9, 0, tzinfo=LIMA))  # 09:00 en Nueva York
CLOSED = FixedClock(datetime(2026, 11, 4, 20, 0, tzinfo=LIMA))
AT = datetime(2026, 11, 4, 8, 55, tzinfo=LIMA)
DOWN = SourceUnavailableError("sin conexión")


def build(
    sources: list[FakeProvider],
    repository: InMemoryPriceRepository,
    clock: FixedClock = OPEN,
    rates: FakeProvider | None = None,
) -> CollectPrices:
    return CollectPrices(
        sources,
        rates or FakeProvider(rate("3.75", clock.today())),
        repository,
        Consensus(),
        PriceValidator(),
        MarketHours(),
        clock,
    )


def test_saves_median_of_sources_with_their_names() -> None:
    repository = InMemoryPriceRepository()

    report = build(
        [source("Yahoo", live("300.10", AT)), source("Stooq", live("300.20", AT))], repository
    ).execute()

    assert report.quotation_saved and report.exchange_rate_saved
    assert repository.live[0].cents_per_pound == Decimal("300.15")
    assert repository.live[0].sources == ("Yahoo", "Stooq")
    # El último precio del día queda como cierre diario
    assert repository.quotations[0].quoted_on == date(2026, 11, 4)


def test_one_source_down_does_not_stop_the_collection() -> None:
    repository = InMemoryPriceRepository()

    report = build([source("Yahoo", DOWN), source("Stooq", live("300", AT))], repository).execute()

    assert report.quotation_saved
    assert report.sources_ok == ["Stooq"]
    assert "Yahoo" in report.issues[0]


def test_discards_disagreeing_source_and_reports_it() -> None:
    repository = InMemoryPriceRepository()
    sources = [
        source("Yahoo", live("300", AT)),
        source("Stooq", live("300", AT)),
        source("Rara", live("310", AT)),
    ]

    report = build(sources, repository).execute()

    assert repository.live[0].cents_per_pound == Decimal("300")
    assert report.sources_discarded == ["Rara"]


def test_all_sources_down_keeps_last_valid_value() -> None:
    repository = InMemoryPriceRepository()
    repository.add_live_quote(live("299", AT - timedelta(minutes=5)))

    report = build([source("Yahoo", DOWN), source("Stooq", DOWN)], repository).execute()

    assert not report.quotation_saved
    assert any("Ninguna fuente" in issue for issue in report.issues)
    assert repository.last_live_quote().cents_per_pound == 299  # type: ignore[union-attr]


def test_does_not_query_sources_with_market_closed() -> None:
    yahoo = source("Yahoo", live("300", AT))

    report = build([yahoo], InMemoryPriceRepository(), CLOSED).execute()

    assert not report.market_open and not report.quotation_saved
    assert yahoo.calls == 0


def test_force_queries_even_with_market_closed() -> None:
    report = build([source("Yahoo", live("300", AT))], InMemoryPriceRepository(), CLOSED).execute(
        force=True
    )

    assert report.quotation_saved


def test_outlier_is_reported_and_not_saved() -> None:
    repository = InMemoryPriceRepository()
    repository.add_live_quote(live("300", AT - timedelta(minutes=1)))

    report = build([source("Yahoo", live("400", AT))], repository).execute()

    assert not report.quotation_saved and len(repository.live) == 1


def test_exchange_rate_is_fetched_once_per_day_with_retries() -> None:
    repository = InMemoryPriceRepository()
    rates = FakeProvider(DOWN, rate("3.75", OPEN.today()))

    build([source("Yahoo", live("300", AT))], repository, rates=rates).execute()
    build(
        [source("Yahoo", live("300.1", AT + timedelta(minutes=1)))], repository, rates=rates
    ).execute()

    assert rates.calls == 2  # 1 falla + 1 éxito; la segunda recolección ya no consulta


def test_exchange_rate_failure_does_not_block_quotation() -> None:
    report = build(
        [source("Yahoo", live("300", AT))],
        InMemoryPriceRepository(),
        rates=FakeProvider(DOWN),
    ).execute()

    assert report.quotation_saved and not report.exchange_rate_saved
