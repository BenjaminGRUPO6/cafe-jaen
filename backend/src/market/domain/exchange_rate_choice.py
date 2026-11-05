"""Qué tipo de cambio usar: el dólar en vivo de hoy (cada minuto) o el oficial del BCRP."""

from bisect import bisect_right
from collections.abc import Sequence
from datetime import date, datetime, tzinfo

from market.domain.quotation import ExchangeRate


def current_rate(
    live: ExchangeRate | None, daily: ExchangeRate | None, today: date, zone: tzinfo | None
) -> ExchangeRate | None:
    """El dólar en vivo si es de hoy (hora de Lima); si no, el último publicado por el BCRP."""
    is_today = (
        live is not None
        and live.rated_at is not None
        and live.rated_at.astimezone(zone).date() == today
    )
    return live if is_today else daily


def rate_at(
    moment: datetime, live: Sequence[ExchangeRate], daily: ExchangeRate | None
) -> ExchangeRate | None:
    """El dólar en vivo vigente en ese momento (el último anterior del mismo día) o el diario.

    `live` debe venir ordenado del más antiguo al más reciente y tener `rated_at`.
    """
    moments = [r.rated_at for r in live if r.rated_at is not None]
    index = bisect_right(moments, moment)
    if index > 0:
        candidate = live[index - 1]
        assert candidate.rated_at is not None
        if candidate.rated_at.astimezone(moment.tzinfo).date() == moment.date():
            return candidate
    return daily
