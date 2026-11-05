from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from market.domain.local_price import CoffeeType, LocalPriceEstimator
from market.domain.ports.price_repository import PriceRepository
from market.domain.quintal_price import TWO_DECIMALS, PriceConverter
from market.domain.quotation import ExchangeRate
from market.domain.source_reading import PriceCollection, ReadingStatus, SourceReading
from shared.domain.ports.clock import Clock

RECENT_DAYS = timedelta(days=30)


@dataclass(frozen=True)
class PriceLogEntry:
    """Una fila del historial: lo que se publicó en una consulta y lo que marcó cada web."""

    at: datetime  # hora de la cotización publicada (o de la consulta, si no se publicó)
    published: bool
    cents_per_pound: Decimal | None
    exchange_rate: Decimal | None
    price_soles: Decimal | None  # bolsa en S/ por quintal (None sin precio o sin tipo de cambio)
    sources: tuple[str, ...]  # webs que respaldaron el precio publicado
    local_soles: dict[CoffeeType, Decimal]  # estimado en Jaén por tipo, con los % actuales
    median_cents: Decimal | None
    readings: tuple[SourceReading, ...]  # vacío en cotizaciones anteriores a este registro


class GetPriceLog:
    """Historial minuto a minuto de la bolsa en un día (pestaña «Bolsa» del equipo).

    Cada fila trae el precio publicado en ¢/lb y en S/ por quintal, el estimado en Jaén por
    tipo de café (con los porcentajes de los últimos 30 días) y lo que marcó cada web, para
    entender por qué se publicó ese valor.
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

    def execute(self, day: date | None = None) -> list[PriceLogEntry]:
        now = self._clock.now()
        start = datetime.combine(day or now.date(), time.min, tzinfo=now.tzinfo)
        end = start + timedelta(days=1)
        rates = {
            r.rated_on: r for r in self._repository.exchange_rates_since(start.date() - RECENT_DAYS)
        }
        ratios = self._current_ratios(now)
        rows = self._rows(start, end)
        entries = []
        for at, cents, sources, collection in rows:
            rate = _rate_for(rates, at.astimezone(now.tzinfo))
            soles = self._converter.to_quintal(cents, rate).soles if cents and rate else None
            entries.append(
                PriceLogEntry(
                    at=at,
                    published=cents is not None,
                    cents_per_pound=cents,
                    exchange_rate=rate,
                    price_soles=soles,
                    sources=sources,
                    local_soles=_local(soles, ratios),
                    median_cents=collection.median_cents if collection else None,
                    readings=collection.readings if collection else (),
                )
            )
        return sorted(entries, key=lambda e: e.at, reverse=True)  # la más reciente primero

    def _rows(
        self, start: datetime, end: datetime
    ) -> list[tuple[datetime, Decimal | None, tuple[str, ...], PriceCollection | None]]:
        collections = self._repository.collections_between(start, end)
        rows: list[tuple[datetime, Decimal | None, tuple[str, ...], PriceCollection | None]] = [
            (
                c.published_quoted_at or c.collected_at,
                c.published_cents,
                tuple(r.source for r in c.readings if r.status is ReadingStatus.USED)
                if c.published
                else (),
                c,
            )
            for c in collections
        ]
        # Cotizaciones guardadas antes de este registro (o cargadas por scripts): sin detalle
        known = {(c.published_quoted_at, c.published_cents) for c in collections if c.published}
        rows += [
            (q.quoted_at, q.cents_per_pound, tuple(q.sources), None)
            for q in self._repository.live_quotes_between(start, end)
            if (q.quoted_at, q.cents_per_pound) not in known
        ]
        return rows

    def _current_ratios(self, now: datetime) -> dict[CoffeeType, Decimal]:
        observations = self._repository.local_observations_since(now - RECENT_DAYS)
        # El estimador con un precio de 1 devuelve directamente el porcentaje de cada tipo
        return {e.coffee_type: e.ratio for e in self._estimator.estimate(Decimal(1), observations)}


def _rate_for(rates: dict[date, ExchangeRate], moment: datetime) -> Decimal | None:
    # El tipo de cambio del día o, si aún no se publicó, el último anterior
    day = moment.date()
    known = [d for d in rates if d <= day]
    return rates[max(known)].soles_per_dollar if known else None


def _local(soles: Decimal | None, ratios: dict[CoffeeType, Decimal]) -> dict[CoffeeType, Decimal]:
    if soles is None:
        return {}
    return {
        coffee_type: (soles * ratio).quantize(TWO_DECIMALS) for coffee_type, ratio in ratios.items()
    }
