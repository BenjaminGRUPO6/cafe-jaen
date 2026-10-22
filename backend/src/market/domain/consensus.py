"""Consenso entre varias webs que publican el mismo precio (HU02)."""

from dataclasses import dataclass
from decimal import Decimal
from statistics import median

from market.domain.errors import NoQuotationError, SourcesDisagreeError
from market.domain.quotation import LiveQuote

DEFAULT_MAX_DEVIATION = Decimal("0.01")  # 1 %


@dataclass(frozen=True)
class ConsensusResult:
    quote: LiveQuote
    discarded: tuple[str, ...]  # fuentes que se alejaron demasiado de la mediana


class Consensus:
    """Publica la mediana de las fuentes y descarta la que se aleja más del máximo permitido."""

    def __init__(self, max_deviation: Decimal = DEFAULT_MAX_DEVIATION) -> None:
        self._max_deviation = max_deviation

    def consolidate(self, quotes: list[LiveQuote]) -> ConsensusResult:
        if not quotes:
            raise NoQuotationError()
        middle = Decimal(median(quote.cents_per_pound for quote in quotes))
        # Una web con un dato raro no debe mover el precio que ve el caficultor
        agreeing = [q for q in quotes if self._deviation(q, middle) <= self._max_deviation]
        if not agreeing:
            raise SourcesDisagreeError([s for q in quotes for s in q.sources])
        discarded = tuple(s for q in quotes if q not in agreeing for s in q.sources)
        price = Decimal(median(q.cents_per_pound for q in agreeing)).quantize(Decimal("0.0001"))
        merged = LiveQuote(
            cents_per_pound=price,
            # La hora publicada es la de la fuente más reciente entre las que coinciden
            quoted_at=max(q.quoted_at for q in agreeing),
            sources=tuple(s for q in agreeing for s in q.sources),
        )
        return ConsensusResult(merged, discarded)

    @staticmethod
    def _deviation(quote: LiveQuote, middle: Decimal) -> Decimal:
        return abs(quote.cents_per_pound - middle) / middle
