"""Fuente 2: Stooq, que publica la última cotización en un CSV público (símbolo KC.F).

El formato y la zona horaria de la hora se verifican en el spike (scripts/spike_sources.py).
"""

import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import httpx

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import LiveQuote

DEFAULT_URL = "https://stooq.com/q/l/?s=kc.f&f=sd2t2c&h&e=csv"
DEFAULT_TIMEZONE = "Europe/Warsaw"  # Stooq publica la hora de Polonia


class StooqQuotationSource:
    """Implementa QuotationSource leyendo el CSV de Stooq."""

    name = "Stooq"

    def __init__(
        self,
        url: str = DEFAULT_URL,
        timezone: str = DEFAULT_TIMEZONE,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._url = url
        self._zone = ZoneInfo(timezone)
        self._timeout = timeout_seconds

    def fetch_latest(self) -> LiveQuote:
        try:
            response = httpx.get(self._url, timeout=self._timeout)
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise SourceUnavailableError(f"no respondió: {error}") from error
        return parse_stooq_csv(response.text, self._zone, self.name)


def parse_stooq_csv(text: str, zone: ZoneInfo, name: str = "Stooq") -> LiveQuote:
    """Convierte «Symbol,Date,Time,Close» en una cotización (falla si viene «N/D»)."""
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise SourceUnavailableError("respuesta vacía")
    row = rows[0]
    try:
        quoted_at = datetime.fromisoformat(f"{row['Date']}T{row['Time']}").replace(tzinfo=zone)
        price = Decimal(row["Close"])
    except (KeyError, ValueError, InvalidOperation) as error:
        raise SourceUnavailableError(f"formato inesperado: {row}") from error
    return LiveQuote(price, quoted_at, (name,))
