"""Fuente 3: CNBC, servicio público de cotizaciones de su web y su app (símbolo @KC.1).

No requiere cuenta ni clave. Entrega el último precio en ¢USD/lb y la hora de la bolsa.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import LiveQuote

DEFAULT_URL = (
    "https://quote.cnbc.com/quote-html-webservice/restQuote/symbolType/symbol"
    "?symbols=%40KC.1&requestMethod=itv&noform=1&partnerId=2&fund=1&exthrs=1&output=json"
)
NEW_YORK = ZoneInfo("America/New_York")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CafeJaen/1.0)"}


class CnbcQuotationSource:
    """Implementa QuotationSource con el servicio de cotizaciones de CNBC."""

    name = "CNBC"

    def __init__(self, url: str = DEFAULT_URL, timeout_seconds: float = 10.0) -> None:
        self._url = url
        self._timeout = timeout_seconds

    def fetch_latest(self) -> LiveQuote:
        try:
            response = httpx.get(self._url, timeout=self._timeout, headers=HEADERS)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise SourceUnavailableError(f"no respondió: {error}") from error
        return parse_cnbc_quote(payload, self.name)


def parse_cnbc_quote(payload: dict[str, Any], name: str = "CNBC") -> LiveQuote:
    """Lee «last» (precio) y «last_time» (hora) de la primera cotización de la respuesta."""
    try:
        quotes = payload["FormattedQuoteResult"]["FormattedQuote"]
        quote = quotes[0] if isinstance(quotes, list) else quotes
        price = Decimal(str(quote["last"]).replace(",", ""))
    except (KeyError, IndexError, TypeError, InvalidOperation) as error:
        raise SourceUnavailableError(f"formato inesperado: {str(payload)[:120]}") from error
    if price <= 0:
        raise SourceUnavailableError("precio no válido")
    return LiveQuote(price, _quote_time(quote.get("last_time")), (name,))


def _quote_time(text: Any) -> datetime:
    # Ej.: «2026-11-05T09:42:05.000-0500»; si no viene, se usa la hora de la consulta
    if isinstance(text, str):
        for pattern in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(text, pattern)
            except ValueError:
                continue
    return datetime.now(NEW_YORK).replace(second=0, microsecond=0)
