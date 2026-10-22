from typing import Protocol

from market.domain.quotation import ExchangeRate, LiveQuote


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
