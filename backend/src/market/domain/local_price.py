"""Precio estimado en Jaén a partir de la bolsa (HU12).

Las cooperativas fijan su precio a partir de la bolsa. El equipo pregunta «¿a cuánto está el
quintal ahora?» y lo anota junto con el precio de la bolsa de ese momento: la relación entre
ambos (porcentaje) permite estimar, en vivo, cuánto se paga en Jaén mientras la bolsa se mueve.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from statistics import median

from market.domain.errors import InvalidLocalPriceError
from market.domain.quintal_price import TWO_DECIMALS

DEFAULT_WINDOW = timedelta(days=30)
MIN_RATIO = Decimal("0.40")  # por debajo, casi seguro es un error al escribir el precio
MAX_RATIO = Decimal("1.20")
FEW_OBSERVATIONS = 3  # con menos, la app avisa que el estimado tiene pocos datos


class CoffeeType(StrEnum):
    """Tipos de café que el caficultor puede filtrar (cada uno con su propio porcentaje)."""

    CONVENTIONAL = "convencional"
    ORGANIC = "organico"  # orgánico / comercio justo
    SPECIALTY = "especial"


@dataclass(frozen=True)
class LocalPriceObservation:
    """Precio que pagaba una cooperativa y el precio de la bolsa en ese mismo momento."""

    observed_at: datetime
    cooperative: str
    coffee_type: CoffeeType
    paid_soles: Decimal  # S/ por quintal que paga la cooperativa al productor
    exchange_soles: Decimal  # precio de la bolsa en S/ por quintal en ese momento

    def __post_init__(self) -> None:
        if not self.cooperative.strip():
            raise InvalidLocalPriceError("Escribe el nombre de la cooperativa")
        if self.paid_soles <= 0 or self.exchange_soles <= 0:
            raise InvalidLocalPriceError("El precio debe ser mayor a cero")
        if not MIN_RATIO <= self.ratio <= MAX_RATIO:
            raise InvalidLocalPriceError(
                f"El precio equivale al {self.ratio * 100:.0f} % de la bolsa: "
                "revisa si está bien escrito"
            )

    @property
    def ratio(self) -> Decimal:
        return self.paid_soles / self.exchange_soles


@dataclass(frozen=True)
class LocalEstimate:
    """Precio estimado en Jaén para un tipo de café, con los datos que lo respaldan."""

    coffee_type: CoffeeType
    ratio: Decimal
    estimated_soles: Decimal
    observations: int
    first_day: date
    last_day: date

    @property
    def few_data(self) -> bool:
        return self.observations < FEW_OBSERVATIONS


class LocalPriceEstimator:
    """Estimado = precio de la bolsa × mediana de los porcentajes de los últimos 30 días."""

    def __init__(self, window: timedelta = DEFAULT_WINDOW) -> None:
        self.window = window

    def estimate(
        self, exchange_soles: Decimal, observations: Sequence[LocalPriceObservation]
    ) -> list[LocalEstimate]:
        estimates = []
        for coffee_type in CoffeeType:
            own = [o for o in observations if o.coffee_type is coffee_type]
            if not own:
                continue  # sin precios anotados para ese tipo no se inventa un estimado
            # La mediana no se deja llevar por un precio raro cuando hay pocos datos
            ratio = Decimal(median(o.ratio for o in own))
            days = sorted(o.observed_at.date() for o in own)
            estimates.append(
                LocalEstimate(
                    coffee_type,
                    ratio.quantize(Decimal("0.0001")),  # se redondea solo para mostrarlo
                    (exchange_soles * ratio).quantize(TWO_DECIMALS),
                    len(own),
                    days[0],
                    days[-1],
                )
            )
        return estimates
