"""Lectura de las respuestas del BCRP (tipo de cambio) y de Stooq (fuente 2 del precio)."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from market.domain.errors import SourceUnavailableError
from market.infrastructure.sources.bcrp_exchange_rate_provider import parse_bcrp_response
from market.infrastructure.sources.stooq_quotation_source import (
    parse_stooq_csv,
    parse_stooq_history,
)

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


# ---------------------------------------------------------------- histórico diario de Stooq
def test_stooq_daily_history_is_read_from_its_csv() -> None:
    text = (
        "Date,Open,High,Low,Close,Volume\n"
        "2026-11-02,395.1,399.0,390.2,397.45,1200\n"
        "2026-11-03,N/D,N/D,N/D,N/D,0\n"
        "2026-11-04,398.0,401.5,396.0,400.10,1500\n"
    )

    history = parse_stooq_history(text)

    assert [(q.quoted_on, q.cents_per_pound) for q in history] == [
        (date(2026, 11, 2), Decimal("397.45")),
        (date(2026, 11, 4), Decimal("400.10")),
    ]
    assert {q.source for q in history} == {"Stooq"}


def test_stooq_history_without_rows_is_a_source_failure() -> None:
    with pytest.raises(SourceUnavailableError):
        parse_stooq_history("No data")


# ---------------------------------------------------------------- CNBC y TradingView
def test_cnbc_quote_is_read_with_the_exchange_time() -> None:
    from market.infrastructure.sources.cnbc_quotation_source import parse_cnbc_quote

    payload = {
        "FormattedQuoteResult": {
            "FormattedQuote": [
                {"symbol": "@KC.1", "last": "280.75", "last_time": "2026-11-05T09:42:05.000-0500"}
            ]
        }
    }

    quote = parse_cnbc_quote(payload)

    assert quote.cents_per_pound == Decimal("280.75")
    assert quote.quoted_at.isoformat() == "2026-11-05T09:42:05-05:00"
    assert quote.sources == ("CNBC",)
    assert quote.has_exchange_time


@pytest.mark.parametrize(
    "payload",
    [{}, {"FormattedQuoteResult": {"FormattedQuote": [{"last": "UNCH"}]}}],
)
def test_unexpected_cnbc_format_is_a_source_failure(payload: dict[str, object]) -> None:
    from market.infrastructure.sources.cnbc_quotation_source import parse_cnbc_quote

    with pytest.raises(SourceUnavailableError):
        parse_cnbc_quote(payload)


def test_tradingview_scan_is_read_without_exchange_time() -> None:
    from market.infrastructure.sources.tradingview_quotation_source import parse_tradingview_scan

    quote = parse_tradingview_scan({"totalCount": 1, "data": [{"s": "ICEUS:KC1!", "d": [280.8]}]})

    assert quote.cents_per_pound == Decimal("280.8")
    assert quote.sources == ("TradingView",)
    assert not quote.has_exchange_time


def test_unexpected_tradingview_format_is_a_source_failure() -> None:
    from market.infrastructure.sources.tradingview_quotation_source import parse_tradingview_scan

    with pytest.raises(SourceUnavailableError):
        parse_tradingview_scan({"data": []})
