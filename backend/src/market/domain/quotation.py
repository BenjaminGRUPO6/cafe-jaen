from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class LiveQuote:
    """Cotización del café arábica en la bolsa de Nueva York (ICE, contrato C) en ¢USD/lb.

    `quoted_at` es la hora en que la bolsa registró ese precio (no la hora de la consulta):
    las webs gratuitas publican con algunos minutos de retraso y el caficultor debe verlo.
    """

    cents_per_pound: Decimal
    quoted_at: datetime
    sources: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.cents_per_pound <= 0:
            raise ValueError("La cotización debe ser mayor a cero")
        if self.quoted_at.tzinfo is None:
            raise ValueError("La hora de la cotización debe tener zona horaria")


@dataclass(frozen=True)
class Quotation:
    """Cierre diario de la bolsa: alimenta el histórico de 30/90 días y el pronóstico."""

    cents_per_pound: Decimal
    quoted_on: date
    source: str


@dataclass(frozen=True)
class ExchangeRate:
    """Tipo de cambio: soles por dólar estadounidense."""

    soles_per_dollar: Decimal
    rated_on: date
    source: str
