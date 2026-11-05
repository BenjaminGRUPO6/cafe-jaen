from datetime import date
from typing import Protocol

from market.domain.quotation import ExchangeRate, LiveQuote, Quotation


class QuotationSource(Protocol):
    """Puerto de salida: una web que publica la cotización de Nueva York (KC).

    Hay un adaptador por web; el Recolector consulta varias y las compara.
    Si la web falla, la implementación debe lanzar SourceUnavailableError.
    """

    name: str

    def fetch_latest(self) -> LiveQuote: ...


class ExchangeRateProvider(Protocol):
    """Puerto de salida: obtiene el tipo de cambio más reciente."""

    def fetch_latest(self) -> ExchangeRate: ...


class DailyHistorySource(Protocol):
    """Puerto de salida: una web con los cierres diarios del contrato C (carga del histórico)."""

    name: str

    def fetch_daily_history(self, start: date) -> list[Quotation]: ...


class ExchangeRateHistoryProvider(Protocol):
    """Puerto de salida: tipos de cambio de un rango de fechas (carga del histórico)."""

    def fetch_history(self, start: date, end: date) -> list[ExchangeRate]: ...
