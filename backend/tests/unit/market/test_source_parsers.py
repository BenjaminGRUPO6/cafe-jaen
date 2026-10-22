"""Lectura de las respuestas del BCRP (tipo de cambio) y de Stooq (fuente 2 del precio)."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from market.domain.errors import SourceUnavailableError
from market.infrastructure.sources.bcrp_exchange_rate_provider import parse_bcrp_response
from market.infrastructure.sources.stooq_quotation_source import parse_stooq_csv

SAMPLE = {
    "config": {"title": "Tipo de cambio"},
    "periods": [
        {"name": "30.Set.26", "values": ["3.742"]},
        {"name": "01.Oct.26", "values": ["n.d."]},
        {"name": "02.Oct.26", "values": ["3.751"]},
    ],
}


def test_parses_spanish_dates_and_skips_missing_values() -> None:
    rates = parse_bcrp_response(SAMPLE)

    assert [(r.rated_on, r.soles_per_dollar) for r in rates] == [
        (date(2026, 9, 30), Decimal("3.742")),
        (date(2026, 10, 2), Decimal("3.751")),
    ]


# ---------------------------------------------------------------- Stooq (fuente 2)
WARSAW = ZoneInfo("Europe/Warsaw")


def test_parses_stooq_csv_with_its_timezone() -> None:
    quote = parse_stooq_csv("Symbol,Date,Time,Close\nKC.F,2026-11-04,15:42:10,385.25\n", WARSAW)

    assert quote.cents_per_pound == Decimal("385.25")
    assert quote.quoted_at == datetime(2026, 11, 4, 15, 42, 10, tzinfo=WARSAW)
    assert quote.sources == ("Stooq",)


@pytest.mark.parametrize(
    "text", ["", "Symbol,Date,Time,Close\nKC.F,N/D,N/D,N/D\n", "otra,cosa\n1,2\n"]
)
def test_unexpected_stooq_format_is_a_source_failure(text: str) -> None:
    with pytest.raises(SourceUnavailableError):
        parse_stooq_csv(text, WARSAW)


# ---------------------------------------------------------------- fuente DEMO (sin internet)
def test_demo_source_moves_a_little_and_is_labeled_synthetic() -> None:
    from market.infrastructure.sources.demo_quotation_source import DemoQuotationSource

    demo = DemoQuotationSource(lambda: Decimal("385"), seed=1)
    first, second = demo.fetch_latest(), demo.fetch_latest()

    assert first.sources == ("DEMO (sintético)",)
    assert abs(first.cents_per_pound - 385) < 3  # parte del último precio conocido
    assert abs(second.cents_per_pound - first.cents_per_pound) < 3
    assert second.quoted_at >= first.quoted_at
