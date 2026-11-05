"""Fuente 4: TradingView, escáner público de su web (contrato continuo ICEUS:KC1!).

No requiere cuenta ni clave. Entrega el último precio en ¢USD/lb; la respuesta no trae la hora
de la cotización, así que se registra la hora de la consulta (redondeada al minuto).
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from market.domain.errors import RateLimitedError, SourceUnavailableError
from market.domain.quotation import LiveQuote

DEFAULT_URL = "https://scanner.tradingview.com/futures/scan"
TICKER = "ICEUS:KC1!"
NEW_YORK = ZoneInfo("America/New_York")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CafeJaen/1.0)"}


class TradingViewQuotationSource:
    """Implementa QuotationSource con el escáner público de TradingView."""

    name = "TradingView"

    def __init__(self, url: str = DEFAULT_URL, timeout_seconds: float = 10.0) -> None:
        self._url = url
        self._timeout = timeout_seconds

    def fetch_latest(self) -> LiveQuote:
        body = {"symbols": {"tickers": [TICKER], "query": {"types": []}}, "columns": ["close"]}
        try:
            response = httpx.post(self._url, json=body, timeout=self._timeout, headers=HEADERS)
            if response.status_code == 429:
                raise RateLimitedError(
                    "pidió esperar: 429 Too Many Requests", _retry_after(response)
                )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise SourceUnavailableError(f"no respondió: {error}") from error
        return parse_tradingview_scan(payload, self.name)


def parse_tradingview_scan(payload: dict[str, Any], name: str = "TradingView") -> LiveQuote:
    """La respuesta trae los valores en el orden de las columnas pedidas: «d»: [close]."""
    try:
        row = next(r for r in payload["data"] if r.get("s") == TICKER)
        price = Decimal(str(row["d"][0]))
    except (KeyError, IndexError, TypeError, StopIteration, InvalidOperation) as error:
        raise SourceUnavailableError(f"formato inesperado: {str(payload)[:120]}") from error
    if price <= 0:
        raise SourceUnavailableError("precio no válido")
    now = datetime.now(NEW_YORK).replace(second=0, microsecond=0)
    return LiveQuote(price, now, (name,), has_exchange_time=False)


def _retry_after(response: httpx.Response) -> float | None:
    """Segundos que la web pide esperar (cabecera Retry-After), si los indica."""
    try:
        return float(response.headers.get("Retry-After", ""))
    except ValueError:
        return None
