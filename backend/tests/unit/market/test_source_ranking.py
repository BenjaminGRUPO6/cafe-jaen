"""Evaluación de las webs: gana la que responde, coincide con las demás y llega más al día."""

from datetime import timedelta
from decimal import Decimal

from market.domain.source_ranking import rank_sources
from market.domain.source_reading import PriceCollection, ReadingStatus, SourceReading
from tests.fakes import FixedClock

NOW = FixedClock().now()


def collection(*readings: SourceReading) -> PriceCollection:
    return PriceCollection(NOW, readings, Decimal("280"), Decimal("280"), NOW)


def used(source: str, delay: int, deviation: str = "0", timed: bool = True) -> SourceReading:
    return SourceReading(
        source,
        ReadingStatus.USED,
        Decimal("280"),
        NOW - timedelta(minutes=delay),
        Decimal(deviation),
        has_exchange_time=timed,
    )


def test_the_fresh_and_reliable_web_ranks_first() -> None:
    failed = SourceReading("Stooq", ReadingStatus.FAILED, detail="timed out")
    discarded = SourceReading("Otra", ReadingStatus.DISCARDED, Decimal("300"), NOW, Decimal("7.1"))
    ranking = rank_sources(
        [
            collection(used("CNBC", 2), used("Yahoo Finance", 25), failed, discarded),
            collection(used("CNBC", 3), used("Yahoo Finance", 26), failed, discarded),
        ]
    )

    assert [s.source for s in ranking] == ["CNBC", "Yahoo Finance", "Otra", "Stooq"]
    cnbc, yahoo, other, stooq = ranking
    assert (cnbc.consultations, cnbc.answered, cnbc.used) == (2, 2, 2)
    assert cnbc.avg_delay_minutes == 2.5
    assert yahoo.avg_delay_minutes == 25.5
    assert other.discarded == 2 and other.avg_deviation_pct == 7.1
    assert stooq.answered == 0 and stooq.score == 0


def test_a_web_without_exchange_time_gets_half_the_freshness_points() -> None:
    (score,) = rank_sources([collection(used("TradingView", 0, timed=False))])

    assert score.avg_delay_minutes is None
    assert score.score == 90.0  # 40 responde + 40 coincide + 10 (actualidad desconocida)
