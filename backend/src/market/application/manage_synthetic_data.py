from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from market.domain.cooperative import Cooperative
from market.domain.errors import MarketError
from market.domain.ports.cooperative_repository import CooperativeRepository
from market.domain.ports.price_repository import PriceRepository
from market.domain.quintal_price import PriceConverter
from market.domain.synthetic_data import (
    SYNTHETIC_LOCATION,
    ExchangeDay,
    generate_observations,
    is_synthetic,
    synthetic_names,
)
from shared.domain.ports.clock import Clock

DEFAULT_DAYS = 60  # dos meses de precios: el estimado usa los últimos 30 días
FIRST_HOUR = time(8, 0)  # el equipo anota los precios desde las 8 a. m. (hora de Lima)


class NoRealExchangeError(MarketError):
    def __init__(self) -> None:
        super().__init__(
            "Primero se necesita el precio real de la bolsa (histórico y tipo de cambio): "
            "espera a que el Recolector lo cargue."
        )


@dataclass(frozen=True)
class SyntheticStatus:
    cooperatives: int
    observations: int


class ManageSyntheticData:
    """Carga o borra los precios SINTÉTICOS de cooperativas para la demostración.

    Los precios de la bolsa que acompañan a cada dato son los reales de ese día; solo lo que
    «pagó» la cooperativa es inventado. Cargar de nuevo reemplaza los sintéticos anteriores.
    """

    def __init__(
        self,
        prices: PriceRepository,
        cooperatives: CooperativeRepository,
        converter: PriceConverter,
        clock: Clock,
    ) -> None:
        self._prices = prices
        self._cooperatives = cooperatives
        self._converter = converter
        self._clock = clock

    def status(self) -> SyntheticStatus:
        names = self._names()
        return SyntheticStatus(len(names), self._prices.count_local_observations_of(names))

    def load(self, days: int = DEFAULT_DAYS) -> SyntheticStatus:
        exchange_days = self._exchange_days(days)
        if not exchange_days:
            raise NoRealExchangeError()
        self.remove()
        names = synthetic_names()
        for name in names:
            self._cooperatives.add(Cooperative.create(name, SYNTHETIC_LOCATION, None))
        self._prices.add_local_observations(generate_observations(exchange_days, names))
        return self.status()

    def remove(self) -> SyntheticStatus:
        names = self._names()
        removed = self._prices.delete_local_observations_of(names)
        for cooperative in self._cooperatives.all():
            if cooperative.id is not None and is_synthetic(cooperative.name):
                self._cooperatives.delete(cooperative.id)
        return SyntheticStatus(len(names), removed)

    def _names(self) -> list[str]:
        return [c.name for c in self._cooperatives.all() if is_synthetic(c.name)]

    def _exchange_days(self, days: int) -> list[ExchangeDay]:
        """Precio real de la bolsa en S/ por quintal de cada día hábil de ese periodo."""
        today = self._clock.today()
        zone = self._clock.now().tzinfo
        result = []
        for close in self._prices.quotations_since(today - timedelta(days=days)):
            rate = self._prices.exchange_rate_on(close.quoted_on)
            if rate is None or close.quoted_on > today:
                continue
            soles = self._converter.to_quintal(close.cents_per_pound, rate.soles_per_dollar).soles
            result.append(ExchangeDay(_morning(close.quoted_on, zone), soles))
        return result


def _morning(day: date, zone: object) -> datetime:
    return datetime.combine(day, FIRST_HOUR, tzinfo=zone)  # type: ignore[arg-type]
