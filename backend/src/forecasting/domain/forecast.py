from dataclasses import dataclass
from datetime import date
from decimal import Decimal

_TWO_DECIMALS = Decimal("0.01")
DISCLAIMER = "Pronóstico referencial: no es una recomendación de venta."


@dataclass(frozen=True)
class ForecastPoint:
    """Precio esperado para un día y su rango (en S/ por quintal)."""

    day: date
    expected: Decimal
    lower: Decimal
    upper: Decimal


@dataclass(frozen=True)
class Forecast:
    """Pronóstico generado por el Agente Predictor (HU06)."""

    generated_on: date
    model_name: str
    mape: Decimal  # error porcentual medio del modelo en la validación
    points: tuple[ForecastPoint, ...]

    @classmethod
    def from_predictions(
        cls,
        generated_on: date,
        model_name: str,
        mape: float,
        days: list[date],
        predictions: list[float],
    ) -> "Forecast":
        """Construye el pronóstico; el rango es ± el error medio que tuvo el modelo."""
        error = Decimal(str(mape)) / 100
        points = []
        for day, value in zip(days, predictions, strict=True):
            expected = Decimal(str(value)).quantize(_TWO_DECIMALS)
            margin = (expected * error).quantize(_TWO_DECIMALS)
            points.append(
                ForecastPoint(day, expected, max(expected - margin, Decimal(0)), expected + margin)
            )
        return cls(
            generated_on, model_name, Decimal(str(mape)).quantize(_TWO_DECIMALS), tuple(points)
        )
