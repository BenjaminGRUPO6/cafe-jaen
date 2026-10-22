"""Regla «¿Vendo ahora o espero?» (HU05).

Es una regla explicable a propósito: el caficultor y el jurado pueden ver por qué se
recomienda algo, y su acierto se mide con una prueba retrospectiva
(scripts/backtest_selling_rule.py).
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

DEFAULT_THRESHOLD = Decimal("0.03")  # 3 %
DISCLAIMER = "Recomendación referencial: la decisión de vender siempre es tuya."


class Verdict(StrEnum):
    SELL_NOW = "Vender ahora"
    WAIT = "Esperar"
    NO_SIGNAL = "Sin señal clara"
    NO_DATA = "Sin datos suficientes"


@dataclass(frozen=True)
class ForecastDay:
    day: date
    expected: Decimal
    lower: Decimal
    upper: Decimal


@dataclass(frozen=True)
class MarketSnapshot:
    """Lo que el Estratega sabe del mercado en este momento."""

    current_price: Decimal  # S/ por quintal
    priced_at: str  # hora de la cotización, tal como la publicó el Analista
    price_is_stale: bool
    forecast: Sequence[ForecastDay]
    forecast_generated_on: date | None


@dataclass(frozen=True)
class SellingAdvice:
    verdict: Verdict
    reason: str
    current_price: Decimal | None = None
    target_day: date | None = None
    target_price: Decimal | None = None
    change_pct: Decimal | None = None


class SellingDecision:
    """Espera si el pronóstico sube más del umbral y su rango no baja del precio actual;
    vende ahora si el pronóstico al final del horizonte cae más del umbral; si no, sin señal."""

    def __init__(self, threshold: Decimal = DEFAULT_THRESHOLD, max_forecast_age_days: int = 4):
        self._threshold = threshold
        self._max_age = max_forecast_age_days

    def decide(self, snapshot: MarketSnapshot, today: date) -> SellingAdvice:
        missing = self._missing_data(snapshot, today)
        if missing:
            return SellingAdvice(Verdict.NO_DATA, missing)

        current = snapshot.current_price
        best = max(snapshot.forecast, key=lambda point: point.expected)
        last = snapshot.forecast[-1]
        rise = _change(current, best.expected)
        if rise > self._threshold and best.lower >= current:
            return self._advice(
                Verdict.WAIT, current, best, rise, _wait_reason(current, best, rise)
            )
        fall = _change(current, last.expected)
        if fall < -self._threshold:
            return self._advice(
                Verdict.SELL_NOW, current, last, fall, _sell_reason(current, last, fall)
            )
        return self._advice(
            Verdict.NO_SIGNAL,
            current,
            last,
            fall,
            _no_signal_reason(current, last, self._threshold),
        )

    def _missing_data(self, snapshot: MarketSnapshot, today: date) -> str | None:
        if snapshot.price_is_stale:
            return "El precio de la bolsa está desactualizado; vuelve a consultar en unos minutos."
        if not snapshot.forecast or snapshot.forecast_generated_on is None:
            return "Todavía no hay pronóstico para comparar."
        if (today - snapshot.forecast_generated_on).days > self._max_age:
            return "El pronóstico está desactualizado; no se puede recomendar."
        return None

    @staticmethod
    def _advice(
        verdict: Verdict, current: Decimal, point: ForecastDay, change: Decimal, reason: str
    ) -> SellingAdvice:
        return SellingAdvice(
            verdict,
            reason,
            current,
            point.day,
            point.expected,
            (change * 100).quantize(Decimal("0.1")),
        )


def _change(current: Decimal, future: Decimal) -> Decimal:
    return (future - current) / current


def _wait_reason(current: Decimal, point: ForecastDay, rise: Decimal) -> str:
    return (
        f"El pronóstico indica que el precio podría subir de S/ {_soles(current)} a "
        f"S/ {_soles(point.expected)} por quintal (+{_pct(rise)} %) hacia el {_day(point.day)}, "
        "y aun en el peor caso estimado no bajaría del precio de hoy. "
        "Si puedes esperar, conviene esperar."
    )


def _sell_reason(current: Decimal, point: ForecastDay, fall: Decimal) -> str:
    return (
        f"El pronóstico indica que el precio podría bajar de S/ {_soles(current)} a "
        f"S/ {_soles(point.expected)} por quintal ({_pct(fall)} %) hacia el {_day(point.day)}. "
        "Si ya tienes el café listo, conviene vender ahora."
    )


def _no_signal_reason(current: Decimal, point: ForecastDay, threshold: Decimal) -> str:
    return (
        f"El pronóstico para el {_day(point.day)} (S/ {_soles(point.expected)}) está cerca del "
        f"precio de hoy (S/ {_soles(current)}): no hay un cambio mayor a {_pct(threshold)} % "
        "que justifique esperar. Vende según lo que necesites."
    )


def _soles(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")


def _pct(value: Decimal) -> str:
    return f"{value * 100:.1f}".replace(".", ",")


def _day(value: date) -> str:
    return value.strftime("%d/%m")
