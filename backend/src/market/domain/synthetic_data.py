"""Precios SINTÉTICOS de cooperativas para la demostración (nunca para el experimento).

Solo se inventa lo que pagan las cooperativas: el precio de la bolsa de cada día es el real
(Yahoo Finance o Stooq, con el tipo de cambio del BCRP). Los nombres llevan «sintético» para que
nadie los confunda con las cooperativas reales de Jaén, y el equipo los carga o los borra desde
«Equipo → Cooperativas».
"""

import random
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from market.domain.local_price import (
    MAX_RATIO,
    MIN_RATIO,
    SYNTHETIC_MARK,
    CoffeeType,
    LocalPriceObservation,
    is_synthetic,
)
from market.domain.quintal_price import TWO_DECIMALS

SYNTHETIC_PREFIX = f"Cooperativa JAENPERU {SYNTHETIC_MARK}"
SYNTHETIC_LOCATION = "Jaén (datos sintéticos de demostración)"
LETTERS = "ABCDEF"

__all__ = ["ExchangeDay", "generate_observations", "is_synthetic", "synthetic_names"]

# Porcentaje típico de la bolsa que se paga por quintal de pergamino, por tipo de café
TYPICAL_RATIO = {
    CoffeeType.CONVENTIONAL: 0.72,
    CoffeeType.ORGANIC: 0.81,
    CoffeeType.SPECIALTY: 0.92,
}
DAILY_PROBABILITY = 0.85  # no todas las cooperativas se consultan todos los días


def synthetic_names(count: int = len(LETTERS)) -> list[str]:
    return [f"{SYNTHETIC_PREFIX} {letter}" for letter in LETTERS[:count]]


@dataclass(frozen=True)
class ExchangeDay:
    """Precio real de la bolsa de un día hábil, en S/ por quintal."""

    moment: datetime  # hora en que se «anota» el precio ese día
    exchange_soles: Decimal


def generate_observations(
    days: Sequence[ExchangeDay], names: Sequence[str], seed: int | None = None
) -> list[LocalPriceObservation]:
    """Cada cooperativa tiene su propio porcentaje por tipo de café y una variación diaria."""
    rng = random.Random(seed)
    # Diferencia propia de cada cooperativa frente al promedio (unas pagan algo más que otras)
    style = {(n, t): rng.gauss(0, 0.015) for n in names for t in CoffeeType}
    observations = []
    for day in days:
        for name in names:
            for coffee_type in CoffeeType:
                if rng.random() > DAILY_PROBABILITY:
                    continue
                ratio = TYPICAL_RATIO[coffee_type] + style[name, coffee_type] + rng.gauss(0, 0.006)
                ratio = min(max(ratio, float(MIN_RATIO) + 0.01), float(MAX_RATIO) - 0.01)
                paid = (day.exchange_soles * Decimal(str(ratio))).quantize(TWO_DECIMALS)
                moment = day.moment + timedelta(minutes=rng.randint(0, 300))
                observations.append(
                    LocalPriceObservation(moment, name, coffee_type, paid, day.exchange_soles)
                )
    return observations
