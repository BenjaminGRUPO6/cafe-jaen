"""Consulta una web con menos frecuencia y respeta sus pedidos de esperar (HTTP 429).

Algunas webs (TradingView) limitan las consultas automáticas que llegan desde servidores
compartidos como Render. Consultarlas cada minuto hace que respondan «429 Too Many Requests»;
con este envoltorio se consultan cada cierto tiempo y, si piden esperar, se pausan. Mientras
tanto la consulta queda como «en pausa» (no como falla) y el precio sale de las demás webs.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from market.domain.errors import RateLimitedError, SourcePausedError
from market.domain.ports.sources import QuotationSource
from market.domain.quotation import LiveQuote

DEFAULT_BACKOFF = timedelta(minutes=15)
MAX_BACKOFF = timedelta(hours=1)


class ThrottledSource:
    """Implementa QuotationSource envolviendo otra web."""

    def __init__(
        self,
        source: QuotationSource,
        every: timedelta,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.name = source.name
        self._source = source
        self._every = every
        self._now = now
        self._next_at: datetime | None = None
        self._backoff = DEFAULT_BACKOFF

    def fetch_latest(self) -> LiveQuote:
        now = self._now()
        if self._next_at is not None and now < self._next_at:
            minutes = max(1, round((self._next_at - now).total_seconds() / 60))
            raise SourcePausedError(f"se consulta de nuevo en {minutes} min (límite de la web)")
        try:
            quote = self._source.fetch_latest()
        except RateLimitedError as error:
            # Pidió esperar: se respeta su tiempo o, si no lo dice, cada vez un poco más
            wait = (
                timedelta(seconds=error.retry_after_seconds)
                if error.retry_after_seconds
                else self._backoff
            )
            self._next_at = now + wait
            self._backoff = min(self._backoff * 2, MAX_BACKOFF)
            raise
        self._next_at = now + self._every
        self._backoff = DEFAULT_BACKOFF
        return quote
