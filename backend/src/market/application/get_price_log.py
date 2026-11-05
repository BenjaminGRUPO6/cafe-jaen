from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from market.domain.local_price import CoffeeType, LocalPriceEstimator
from market.domain.ports.price_repository import PriceRepository
from market.domain.quintal_price import TWO_DECIMALS, PriceConverter
from market.domain.quotation import ExchangeRate
from shared.domain.ports.clock import Clock

WINDOW = timedelta(hours=24)
RECENT_DAYS = timedelta(days=30)


@dataclass(frozen=True)
class PriceLogEntry:
    quoted_at: datetime
    cents_per_pound: Decimal
    exchange_rate: Decimal | None
    price_soles: Decimal | None  # bolsa en S/ por quintal (sin tipo de cambio de ese día: None)
    sources: tuple[str, ...]
    local_soles: dict[CoffeeType, Decimal]  # estimado en Jaén por tipo, con los % actuales


class GetPriceLog:
    """Historial de lo que consultó el Recolector en las últimas 24 horas (pantalla del equipo).

    Para cada cotización muestra la bolsa en ¢/lb y en S/ por quintal y el estimado en Jaén
    por tipo de café, calculado con los porcentajes de los últimos 30 días.
    """

    def __init__(
        self,
        repository: PriceRepository,
        converter: PriceConverter,
        estimator: LocalPriceEstimator,
        clock: Clock,
    ) -> None:
        self._repository = repository
        self._converter = converter
        self._estimator = estimator
        self._clock = clock

    def execute(self, limit: int) -> list[PriceLogEntry]:
        now = self._clock.now()
        quotes = self._repository.live_quotes_between(now - WINDOW, now)[-limit:]
        since = now.date() - RECENT_DAYS
        rates = {r.rated_on: r for r in self._repository.exchange_rates_since(since)}
        ratios = self._current_ratios(now)
        entries = []
        for quote in reversed(quotes):  # la más reciente primero
            rate = _rate_for(rates, quote.quoted_at)
            soles = self._converter.to_quintal(quote.cents_per_pound, rate).soles if rate else None
            entries.append(
                PriceLogEntry(
                    quote.quoted_at,
                    quote.cents_per_pound,
                    rate,
                    soles,
                    tuple(quote.sources),
                    _local(soles, ratios),
                )
            )
        return entries

    def _current_ratios(self, now: datetime) -> dict[CoffeeType, Decimal]:
        observations = self._repository.local_observations_since(now - RECENT_DAYS)
        # El estimador con un precio de 1 devuelve directamente el porcentaje de cada tipo
        return {e.coffee_type: e.ratio for e in self._estimator.estimate(Decimal(1), observations)}


def _rate_for(rates: dict[date, ExchangeRate], quoted_at: datetime) -> Decimal | None:
    # El tipo de cambio del día o, si aún no se publicó, el último anterior
    day = quoted_at.date()
    known = [d for d in rates if d <= day]
    return rates[max(known)].soles_per_dollar if known else None


def _local(soles: Decimal | None, ratios: dict[CoffeeType, Decimal]) -> dict[CoffeeType, Decimal]:
    if soles is None:
        return {}
    return {
        coffee_type: (soles * ratio).quantize(TWO_DECIMALS) for coffee_type, ratio in ratios.items()
    }
