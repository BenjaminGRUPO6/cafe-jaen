"""Prueba retrospectiva de la regla de venta (T30): ¿qué tan seguido acertó en el pasado?"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal

from decision.domain.selling_decision import Verdict


def was_right(verdict: Verdict, current: Decimal, next_days: Sequence[Decimal]) -> bool | None:
    """Pregunta: «si esperaba hasta el final del horizonte, ¿hubiera recibido más?».

    Esperar acierta si el precio al final fue mayor al de hoy; vender ahora acierta si no.
    Las demás respuestas no se califican.
    """
    if not next_days:
        return None
    better_later = next_days[-1] > current
    if verdict is Verdict.WAIT:
        return better_later
    if verdict is Verdict.SELL_NOW:
        return not better_later
    return None


@dataclass
class BacktestResult:
    counts: dict[Verdict, int] = field(default_factory=lambda: dict.fromkeys(Verdict, 0))
    hits: dict[Verdict, int] = field(default_factory=lambda: dict.fromkeys(Verdict, 0))
    always_sell_hits: int = 0  # referencia: «vender siempre de inmediato»
    days: int = 0

    def add(self, verdict: Verdict, current: Decimal, next_days: Sequence[Decimal]) -> None:
        self.days += 1
        self.counts[verdict] += 1
        if was_right(verdict, current, next_days):
            self.hits[verdict] += 1
        if was_right(Verdict.SELL_NOW, current, next_days):
            self.always_sell_hits += 1

    @property
    def scored(self) -> int:
        return self.counts[Verdict.WAIT] + self.counts[Verdict.SELL_NOW]

    @property
    def hit_rate_pct(self) -> float | None:
        if self.scored == 0:
            return None
        hits = self.hits[Verdict.WAIT] + self.hits[Verdict.SELL_NOW]
        return round(hits / self.scored * 100, 1)

    @property
    def always_sell_rate_pct(self) -> float | None:
        return round(self.always_sell_hits / self.days * 100, 1) if self.days else None
