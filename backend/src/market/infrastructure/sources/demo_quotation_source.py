"""Fuente SINTÉTICA para desarrollo sin internet (QUOTATION_SOURCES=["demo"]).

Simula una cotización que se mueve un poco en cada consulta, partiendo del último precio
guardado para que no parezca un salto atípico. NUNCA usar en el experimento.
"""

import random
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

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
