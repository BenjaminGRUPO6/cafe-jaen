from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

KG_PER_QUINTAL = Decimal("46")
POUNDS_PER_KG = Decimal("2.20462262")
CENTS_PER_DOLLAR = Decimal("100")
TWO_DECIMALS = Decimal("0.01")


@dataclass(frozen=True)
class QuintalPrice:
    """Precio del café en soles por quintal de 46 kg (objeto de valor inmutable)."""

    soles: Decimal

    def __post_init__(self) -> None:
        # Un precio negativo solo puede venir de un error en la fuente de datos
        if self.soles < 0:
            raise ValueError("El precio no puede ser negativo")


class PriceConverter:
    """Convierte la cotización internacional (¢USD/lb) a soles por quintal."""

    def __init__(self, local_factor: Decimal = Decimal("1")) -> None:
        # Ajuste local (diferencial y rendimiento); se configura, no se codifica
        self._local_factor = local_factor

    def to_quintal(self, cents_per_pound: Decimal, exchange_rate: Decimal) -> QuintalPrice:
        usd_per_pound = cents_per_pound / CENTS_PER_DOLLAR
        pounds_per_quintal = KG_PER_QUINTAL * POUNDS_PER_KG
        soles = usd_per_pound * pounds_per_quintal * exchange_rate * self._local_factor
        return QuintalPrice(soles.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP))
