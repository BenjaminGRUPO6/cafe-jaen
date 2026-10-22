from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from market.domain.local_price import LocalEstimate
from market.domain.quintal_price import TWO_DECIMALS, QuintalPrice


@dataclass(frozen=True)
class LivePrice:
    """Precio en vivo tipo bolsa y su variación respecto al cierre anterior (HU03)."""

    quoted_at: datetime
    cents_per_pound: Decimal
    price: QuintalPrice
    previous_close: QuintalPrice | None
    sources: tuple[str, ...]
    market_open: bool
    stale: bool  # la bolsa está abierta pero el último precio es muy antiguo
    local_estimates: tuple[LocalEstimate, ...] = ()  # precio estimado en Jaén por tipo (HU12)

    @property
    def change_soles(self) -> Decimal | None:
        if self.previous_close is None:
            return None
        return self.price.soles - self.previous_close.soles

    @property
    def change_pct(self) -> Decimal | None:
        if self.previous_close is None or self.previous_close.soles == 0:
            return None
        change = (self.price.soles - self.previous_close.soles) / self.previous_close.soles * 100
        return change.quantize(TWO_DECIMALS)


@dataclass(frozen=True)
class HistoryPoint:
    """Un punto del histórico diario (HU04)."""

    priced_on: date
    price: QuintalPrice


@dataclass(frozen=True)
class IntradayPoint:
    """Un punto del gráfico de hoy, minuto a minuto (HU04)."""

    quoted_at: datetime
    price: QuintalPrice
