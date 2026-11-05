"""Registro de cada consulta del Recolector: qué marcó cada web y por qué se publicó ese precio.

El equipo lo revisa en «Equipo → Bolsa» para entender el consenso: el precio publicado es la
mediana de las webs que coinciden (±1 %); las que se alejan se descartan y las que no
respondieron quedan anotadas con su motivo.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from market.domain.consensus import ConsensusResult
from market.domain.quotation import LiveQuote


class CollectionOutcome(StrEnum):
    PUBLISHED = "publicada"  # hay un precio nuevo para el caficultor
    UNCHANGED = "sin cambios"  # las webs repiten la última cotización ya publicada
    REJECTED = "no publicada"  # las webs no coincidieron o el salto fue atípico
    NO_DATA = "sin datos"  # ninguna web respondió


class ReadingStatus(StrEnum):
    USED = "usada"  # coincidió con las demás y entró en la mediana
    DISCARDED = "descartada"  # se alejó más del máximo permitido de la mediana
    FAILED = "sin respuesta"  # la web no respondió o su dato no se pudo leer
    PAUSED = "en pausa"  # no se consultó esta vez, para respetar el límite de la web


@dataclass(frozen=True)
class SourceReading:
    """Lo que entregó una web en una consulta."""

    source: str
    status: ReadingStatus
    cents_per_pound: Decimal | None = None
    quoted_at: datetime | None = None  # hora de la cotización según esa web
    deviation_pct: Decimal | None = None  # distancia a la mediana de todas las webs, en %
    detail: str | None = None  # motivo si no respondió
    has_exchange_time: bool = True  # False si la web no informa la hora de la bolsa


@dataclass(frozen=True)
class PriceCollection:
    """Una consulta completa: las lecturas de cada web y el precio que se publicó (si hubo)."""

    collected_at: datetime
    readings: tuple[SourceReading, ...]
    median_cents: Decimal | None  # mediana de todas las webs que respondieron
    published_cents: Decimal | None  # None si no se publicó (p. ej., las webs no coincidieron)
    published_quoted_at: datetime | None
    outcome: CollectionOutcome = CollectionOutcome.PUBLISHED
    detail: str | None = None  # motivo cuando no se publicó

    @property
    def published(self) -> bool:
        return self.published_cents is not None


def build_collection(
    collected_at: datetime,
    quotes: Sequence[LiveQuote],
    failures: Sequence[tuple[str, str]],
    result: ConsensusResult | None,
    median_cents: Decimal | None,
    published: LiveQuote | None,
    outcome: CollectionOutcome = CollectionOutcome.PUBLISHED,
    detail: str | None = None,
    paused: Sequence[tuple[str, str]] = (),
) -> PriceCollection:
    """Arma el registro de una consulta a partir de lo que respondió cada web.

    `result` es el consenso (None si las webs no coincidieron) y `published` el precio que
    finalmente se guardó (None si la validación lo rechazó, p. ej., por un salto atípico).
    """
    discarded = set(result.discarded) if result else {s for q in quotes for s in q.sources}
    readings = [
        SourceReading(
            source=source,
            status=ReadingStatus.DISCARDED if source in discarded else ReadingStatus.USED,
            cents_per_pound=quote.cents_per_pound,
            quoted_at=quote.quoted_at,
            deviation_pct=_deviation(quote.cents_per_pound, median_cents),
            has_exchange_time=quote.has_exchange_time,
        )
        for quote in quotes
        for source in quote.sources
    ]
    readings += [
        SourceReading(source=name, status=ReadingStatus.FAILED, detail=reason[:200])
        for name, reason in failures
    ]
    readings += [
        SourceReading(source=name, status=ReadingStatus.PAUSED, detail=reason[:200])
        for name, reason in paused
    ]
    return PriceCollection(
        collected_at=collected_at,
        readings=tuple(readings),
        median_cents=median_cents,
        published_cents=published.cents_per_pound if published else None,
        published_quoted_at=published.quoted_at if published else None,
        outcome=outcome,
        detail=detail[:200] if detail else None,
    )


def _deviation(cents: Decimal, median_cents: Decimal | None) -> Decimal | None:
    if not median_cents:
        return None
    return ((cents - median_cents) / median_cents * 100).quantize(Decimal("0.01"))
