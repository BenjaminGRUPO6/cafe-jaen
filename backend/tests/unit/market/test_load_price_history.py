"""Carga del histórico REAL: Yahoo Finance y, si no responde, Stooq; tipo de cambio del BCRP."""

from datetime import date, timedelta
from decimal import Decimal

from market.application.load_price_history import LoadPriceHistory
from market.domain.errors import SourceUnavailableError
from market.domain.quotation import ExchangeRate, Quotation
from tests.fakes import FixedClock, InMemoryPriceRepository

CLOCK = FixedClock()
TODAY = CLOCK.today()


class HistorySource:
    def __init__(self, name: str, closes: list[Quotation] | None) -> None:
        self.name = name
        self._closes = closes
        self.calls = 0

    def fetch_daily_history(self, start: date) -> list[Quotation]:
        self.calls += 1
        if self._closes is None:
            raise SourceUnavailableError("no respondió")
        return [q for q in self._closes if q.quoted_on >= start]


class Rates:
    def fetch_history(self, start: date, end: date) -> list[ExchangeRate]:
        return [ExchangeRate(Decimal("3.75"), end, "BCRP")]


def closes(n: int, source: str) -> list[Quotation]:
    return [Quotation(Decimal("300"), TODAY - timedelta(days=i), source) for i in range(n)]


def test_uses_stooq_when_yahoo_does_not_answer() -> None:
    prices = InMemoryPriceRepository()
    yahoo, stooq = (
        HistorySource("Yahoo Finance", None),
        HistorySource("Stooq", closes(400, "Stooq")),
    )

    report = LoadPriceHistory([yahoo, stooq], Rates(), prices, CLOCK).execute(years=1)

    assert report.source == "Stooq"
    assert report.closes_saved == 366  # un año hacia atrás, sin repetir días
    assert report.rates_saved == 2  # una consulta por cada año calendario del rango
    assert report.issues == ["Yahoo Finance: no respondió"]


def test_does_nothing_when_the_history_is_already_loaded() -> None:
    prices = InMemoryPriceRepository()
    for quotation in closes(200, "Yahoo Finance"):
        prices.save_daily_close(quotation)
    yahoo = HistorySource("Yahoo Finance", closes(400, "Yahoo Finance"))

    report = LoadPriceHistory([yahoo], Rates(), prices, CLOCK).execute(years=5)

    assert report.skipped
    assert yahoo.calls == 0


def test_never_replaces_an_existing_close_and_reports_when_no_web_answers() -> None:
    prices = InMemoryPriceRepository()
    prices.save_daily_close(Quotation(Decimal("310"), TODAY, "Yahoo Finance"))

    report = LoadPriceHistory(
        [HistorySource("Yahoo Finance", None), HistorySource("Stooq", None)],
        Rates(),
        prices,
        CLOCK,
    ).execute(years=1)

    assert report.closes_saved == 0
    assert report.source is None
    assert "Ninguna web entregó el histórico de cierres" in report.issues
    assert prices.quotations == [Quotation(Decimal("310"), TODAY, "Yahoo Finance")]
