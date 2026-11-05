"""Evaluación de las webs de la bolsa: cuál respondió más, coincidió más y llegó más al día.

Sirve para elegir la mejor fuente con datos (pestaña «Equipo → Bolsa»): el precio publicado
siempre es la mediana de las webs que coinciden, pero el equipo ve qué web conviene mantener.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from statistics import mean

from market.domain.source_reading import PriceCollection, ReadingStatus, SourceReading

# Pesos del puntaje (0–100): que responda, que coincida con las demás y que esté al día
ANSWER_WEIGHT, AGREEMENT_WEIGHT, FRESHNESS_WEIGHT = 40, 40, 20
STALE_MINUTES = 60  # con este retraso promedio o más, no suma puntos de actualidad
UNKNOWN_FRESHNESS = 0.5  # sin hora de la bolsa no se sabe si está al día: medio puntaje

Observation = tuple[PriceCollection, SourceReading]


@dataclass(frozen=True)
class SourceScore:
    source: str
    consultations: int
    answered: int
    used: int
    discarded: int
    paused: int  # veces que no se consultó para respetar el límite de la web (no cuentan)
    avg_delay_minutes: float | None  # None si la web no informa la hora de la bolsa
    avg_deviation_pct: float | None  # distancia promedio a la mediana, en valor absoluto
    score: float  # 0–100


def rank_sources(collections: Sequence[PriceCollection]) -> list[SourceScore]:
    """Puntaje de cada web en esas consultas, de la mejor a la peor."""
    by_source: dict[str, list[Observation]] = {}
    for collection in collections:
        for reading in collection.readings:
            by_source.setdefault(reading.source, []).append((collection, reading))
    scores = [_score(source, observations) for source, observations in by_source.items()]
    return sorted(scores, key=lambda s: (-s.score, s.source))


def _score(source: str, all_observations: list[Observation]) -> SourceScore:
    # Las pausas no son consultas: no suben ni bajan el puntaje
    paused = sum(1 for _, r in all_observations if r.status is ReadingStatus.PAUSED)
    observations = [(c, r) for c, r in all_observations if r.status is not ReadingStatus.PAUSED]
    if not observations:
        return SourceScore(source, 0, 0, 0, 0, paused, None, None, 0.0)
    answered = [(c, r) for c, r in observations if r.status is not ReadingStatus.FAILED]
    used = sum(1 for _, r in observations if r.status is ReadingStatus.USED)
    discarded = sum(1 for _, r in observations if r.status is ReadingStatus.DISCARDED)
    delays = [
        max(0.0, (c.collected_at - r.quoted_at).total_seconds() / 60)
        for c, r in answered
        if r.quoted_at is not None and r.has_exchange_time
    ]
    deviations = [abs(float(r.deviation_pct)) for _, r in answered if r.deviation_pct is not None]
    avg_delay = mean(delays) if delays else None
    answer_rate = len(answered) / len(observations)
    agreement = used / len(answered) if answered else 0.0
    if not answered:
        freshness = 0.0  # nunca respondió: no hay nada al día
    elif avg_delay is None:
        freshness = UNKNOWN_FRESHNESS
    else:
        freshness = max(0.0, 1 - avg_delay / STALE_MINUTES)
    score = (
        ANSWER_WEIGHT * answer_rate + AGREEMENT_WEIGHT * agreement + FRESHNESS_WEIGHT * freshness
    )
    return SourceScore(
        source=source,
        consultations=len(observations),
        answered=len(answered),
        used=used,
        discarded=discarded,
        paused=paused,
        avg_delay_minutes=round(avg_delay, 1) if avg_delay is not None else None,
        avg_deviation_pct=round(mean(deviations), 2) if deviations else None,
        score=round(score, 1),
    )
