"""Fuente 1: Yahoo Finance (librería yfinance), símbolo KC=F (café arábica, contrato C)."""

from datetime import date
from decimal import Decimal

import yfinance as yf

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import LiveQuote, Quotation

TICKER = "KC=F"


class YahooQuotationSource:
    """Implementa QuotationSource con la cotización minuto a minuto de Yahoo Finance."""

    name = "Yahoo Finance"

    def fetch_latest(self) -> LiveQuote:
        frame = self._download(period="1d", interval="1m")
        timestamp, close = frame.index[-1], frame["Close"].iloc[-1]
        # El índice ya trae la zona horaria de la bolsa (Nueva York)
        return LiveQuote(
            Decimal(str(round(float(close), 4))), timestamp.to_pydatetime(), (self.name,)
        )

    def fetch_daily_history(self, start: date) -> list[Quotation]:
        """Cierres diarios desde `start` (lo usa el script de carga inicial)."""
        frame = self._download(start=start.isoformat())
        return [
            Quotation(Decimal(str(round(float(close), 4))), index.date(), self.name)
            for index, close in frame["Close"].items()
        ]

    def _download(self, **kwargs: str):  # type: ignore[no-untyped-def]
        try:
            frame = yf.Ticker(TICKER).history(**kwargs)
        except Exception as error:  # yfinance lanza distintos tipos de error de red
            raise SourceUnavailableError(f"no respondió: {error}") from error
        if frame.empty:
            raise SourceUnavailableError("no devolvió cotizaciones")
        return frame
