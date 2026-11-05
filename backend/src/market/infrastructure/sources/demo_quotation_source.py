"""Fuentes SINTÉTICAS para la demostración y el desarrollo sin internet.

Simula una cotización que se mueve un poco en cada consulta, partiendo del último precio
guardado para que no parezca un salto atípico. NUNCA usar en el experimento.
"""

import random
import time
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import LiveQuote

DEFAULT_START_CENTS = 300.0


class DemoQuotationSource:
    """Implementa QuotationSource con una caminata aleatoria."""

    name = "DEMO (sintético)"

    def __init__(
        self,
        last_known: Callable[[], Decimal | None] = lambda: None,
        seed: int | None = None,
    ) -> None:
        self._last_known = last_known
        self._cents: float | None = None
        self._random = random.Random(seed)

    def fetch_latest(self) -> LiveQuote:
        if self._cents is None:
            known = self._last_known()
            self._cents = float(known) if known is not None else DEFAULT_START_CENTS
        self._cents *= 1 + self._random.gauss(0, 0.0008)
        now = datetime.now(ZoneInfo("America/New_York"))
        return LiveQuote(Decimal(f"{self._cents:.2f}"), now, (self.name,))


DEMO_PANEL_NAMES = ("DEMO A (sintético)", "DEMO B (sintético)", "DEMO C (sintético)")
STEP_SECONDS = 30.0  # en una misma consulta las tres webs ven el mismo precio de base


class DemoMarket:
    """Precio de base que comparten las webs simuladas (una caminata aleatoria lenta)."""

    def __init__(
        self,
        last_known: Callable[[], Decimal | None] = lambda: None,
        seed: int | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._last_known = last_known
        self._random = random.Random(seed)
        self._clock = clock
        self._cents: float | None = None
        self._moved_at = -STEP_SECONDS

    def current(self) -> float:
        if self._cents is None:
            known = self._last_known()
            self._cents = float(known) if known is not None else DEFAULT_START_CENTS
        now = self._clock()
        if now - self._moved_at >= STEP_SECONDS:
            self._cents *= 1 + self._random.gauss(0, 0.0008)
            self._moved_at = now
        return self._cents


class DemoPanelSource:
    """Una de varias webs SINTÉTICAS que publican el mismo precio con pequeñas diferencias.

    Sirve para ver el consenso en la demostración: de vez en cuando una web se aleja (y el
    Recolector la descarta) o no responde, como pasa con las webs reales.
    """

    def __init__(
        self,
        name: str,
        market: DemoMarket,
        outlier_rate: float = 0.0,
        failure_rate: float = 0.0,
        seed: int | None = None,
    ) -> None:
        self.name = name
        self._market = market
        self._outlier_rate = outlier_rate
        self._failure_rate = failure_rate
        self._random = random.Random(seed)

    def fetch_latest(self) -> LiveQuote:
        if self._random.random() < self._failure_rate:
            raise SourceUnavailableError("no respondió a tiempo (simulado)")
        cents = self._market.current() * (1 + self._random.gauss(0, 0.0004))
        if self._random.random() < self._outlier_rate:
            # Dato atípico: se aleja entre 1,5 % y 3 % de las demás webs
            cents *= 1 + self._random.choice((-1, 1)) * self._random.uniform(0.015, 0.03)
        now = datetime.now(ZoneInfo("America/New_York"))
        return LiveQuote(Decimal(f"{cents:.2f}"), now, (self.name,))


def demo_panel(last_known: Callable[[], Decimal | None]) -> list[DemoPanelSource]:
    """Las tres webs sintéticas del modo demostración (QUOTATION_SOURCES=["demo"])."""
    market = DemoMarket(last_known)
    a, b, c = DEMO_PANEL_NAMES
    return [
        DemoPanelSource(a, market),
        DemoPanelSource(b, market, outlier_rate=0.08),
        DemoPanelSource(c, market, failure_rate=0.05),
    ]
