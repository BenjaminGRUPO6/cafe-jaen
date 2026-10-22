from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from market.application.get_live_price import GetLivePrice
from market.domain.errors import InvalidLocalPriceError
from market.domain.local_price import CoffeeType, LocalPriceObservation
from market.domain.ports.price_repository import PriceRepository
from shared.domain.ports.clock import Clock

RECENT_DAYS = 30


@dataclass(frozen=True)
class RecordLocalPriceCommand:
    cooperative: str
    coffee_type: str
    paid_soles: str


class RecordLocalPrice:
    """HU12: el equipo anota cuánto paga una cooperativa; se guarda junto a la bolsa del momento."""

    def __init__(
        self, repository: PriceRepository, get_live_price: GetLivePrice, clock: Clock
    ) -> None:
        self._repository = repository
        self._get_live_price = get_live_price
        self._clock = clock

    def execute(self, command: RecordLocalPriceCommand) -> LocalPriceObservation:
        try:
            coffee_type = CoffeeType(command.coffee_type)
            paid = Decimal(command.paid_soles)
        except (ValueError, InvalidOperation):
            raise InvalidLocalPriceError("Revisa el tipo de café y el precio") from None
        # El porcentaje solo tiene sentido con la bolsa de ese mismo momento
        exchange = self._get_live_price.execute().price.soles
        observation = LocalPriceObservation(
            self._clock.now(), command.cooperative.strip(), coffee_type, paid, exchange
        )
        self._repository.add_local_observation(observation)
        return observation

    def recent(self) -> list[LocalPriceObservation]:
        """Precios anotados en los últimos 30 días (para revisarlos en la pantalla del equipo)."""
        return self._repository.local_observations_since(
            self._clock.now() - timedelta(days=RECENT_DAYS)
        )
