"""Dólar en soles (USD/PEN) minuto a minuto desde webs reales y gratuitas.

El BCRP publica el tipo de cambio una sola vez al día; para que el precio en soles siga al dólar
durante la jornada, el Recolector consulta también estas webs cada minuto (la primera que
responda). Si ninguna responde, la app usa el tipo de cambio del BCRP del día.
"""

import logging
from collections.abc import Callable, Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

import httpx
import yfinance as yf

from market.domain.errors import SourceUnavailableError
from market.domain.ports.sources import LiveExchangeRateSource
from market.domain.quotation import ExchangeRate

logger = logging.getLogger(__name__)

LIMA = ZoneInfo("America/Lima")
# Un dólar entre S/ 2,5 y S/ 5,5: fuera de ese rango el dato está mal publicado
PLAUSIBLE = (Decimal("2.5"), Decimal("5.5"))
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CafeJaen/1.0)"}
DEFAULT_SOURCES = ("yahoo", "tradingview")


class YahooExchangeRateSource:
    """Implementa LiveExchangeRateSource con Yahoo Finance, símbolo PEN=X (USD/PEN)."""

    name = "Yahoo Finance (USD/PEN)"
    ticker = "PEN=X"

    def fetch_latest(self) -> ExchangeRate:
        try:
            frame = yf.Ticker(self.ticker).history(period="1d", interval="1m")
        except Exception as error:  # yfinance lanza distintos tipos de error de red
            raise SourceUnavailableError(f"no respondió: {error}") from error
        if frame.empty:
            raise SourceUnavailableError("no devolvió el dólar")
        timestamp, close = frame.index[-1], frame["Close"].iloc[-1]
        return build_rate(
            Decimal(str(round(float(close), 4))), timestamp.to_pydatetime(), self.name
        )


class TradingViewExchangeRateSource:
    """Implementa LiveExchangeRateSource con el escáner público de TradingView (FX_IDC:USDPEN)."""

    name = "TradingView (USD/PEN)"
    ticker = "FX_IDC:USDPEN"

    def __init__(
        self, url: str = "https://scanner.tradingview.com/forex/scan", timeout: float = 10.0
    ) -> None:
        self._url = url
        self._timeout = timeout

    def fetch_latest(self) -> ExchangeRate:
        body = {"symbols": {"tickers": [self.ticker], "query": {"types": []}}, "columns": ["close"]}
        try:
            response = httpx.post(self._url, json=body, timeout=self._timeout, headers=HEADERS)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise SourceUnavailableError(f"no respondió: {error}") from error
        return parse_tradingview_rate(payload, self.ticker, self.name)


def parse_tradingview_rate(payload: dict[str, Any], ticker: str, name: str) -> ExchangeRate:
    """La respuesta trae «d»: [close]; no trae la hora, se usa la de la consulta (al minuto)."""
    try:
        row = next(r for r in payload["data"] if r.get("s") == ticker)
        value = Decimal(str(row["d"][0]))
    except (KeyError, IndexError, TypeError, StopIteration, InvalidOperation) as error:
        raise SourceUnavailableError(f"formato inesperado: {str(payload)[:120]}") from error
    return build_rate(value, datetime.now(LIMA).replace(second=0, microsecond=0), name)


def build_rate(value: Decimal, rated_at: datetime, name: str) -> ExchangeRate:
    """Valida que el dólar sea razonable y lo arma con la fecha de Lima."""
    if not PLAUSIBLE[0] <= value <= PLAUSIBLE[1]:
        raise SourceUnavailableError(f"dólar no válido: {value}")
    local = rated_at.astimezone(LIMA)
    return ExchangeRate(value, local.date(), name, rated_at=local)


def build_exchange_sources(names: Sequence[str]) -> list[LiveExchangeRateSource]:
    """Un adaptador por web configurada (`EXCHANGE_RATE_SOURCES`); los nombres desconocidos se
    ignoran con un aviso y, si no queda ninguno válido, se usan Yahoo Finance y TradingView."""
    available: dict[str, Callable[[], LiveExchangeRateSource]] = {
        "yahoo": YahooExchangeRateSource,
        "tradingview": TradingViewExchangeRateSource,
    }
    unknown = [name for name in names if name not in available]
    if unknown:
        logger.warning("EXCHANGE_RATE_SOURCES tiene webs desconocidas %s: se ignoran", unknown)
    valid = [name for name in dict.fromkeys(names) if name in available] or list(DEFAULT_SOURCES)
    return [available[name]() for name in valid]
