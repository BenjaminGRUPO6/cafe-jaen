from datetime import date, datetime
from typing import Protocol

from market.domain.local_price import LocalPriceObservation
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation


class PriceRepository(Protocol):
    # ---- cotizaciones en vivo (cada minuto)
    def add_live_quote(self, quote: LiveQuote) -> None: ...

    def last_live_quote(self) -> LiveQuote | None: ...

    def live_quotes_between(self, start: datetime, end: datetime) -> list[LiveQuote]:
        """Cotizaciones en vivo en ese intervalo, de la más antigua a la más reciente."""
        ...

    # ---- cierres diarios (histórico y pronóstico)
    def save_daily_close(self, quotation: Quotation) -> None:
        """Guarda o reemplaza el cierre de ese día con el último precio conocido."""
        ...

    def last_quotations(self, limit: int) -> list[Quotation]:
        """Últimos cierres diarios, del más reciente al más antiguo."""
        ...

    def quotations_since(self, day: date) -> list[Quotation]:
        """Cierres diarios desde esa fecha, ordenados del más antiguo al más reciente."""
        ...

    # ---- tipo de cambio
    def add_exchange_rate(self, rate: ExchangeRate) -> None:
        """Guarda o reemplaza el tipo de cambio de esa fecha."""
        ...

    def exchange_rate_on(self, day: date) -> ExchangeRate | None:
        """Tipo de cambio vigente ese día (el último publicado hasta esa fecha)."""
        ...

    def exchange_rates_since(self, day: date) -> list[ExchangeRate]: ...

    # ---- precios de cooperativas (HU12)
    def add_local_observation(self, observation: LocalPriceObservation) -> None: ...

    def local_observations_since(self, moment: datetime) -> list[LocalPriceObservation]:
        """Precios anotados desde ese momento, del más reciente al más antiguo."""
        ...
