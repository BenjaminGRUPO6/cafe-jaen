from typing import Any

from decision.application.get_selling_advice import GetSellingAdvice
from decision.domain.selling_decision import DISCLAIMER, SellingAdvice
from shared.domain.agent_message import AgentMessage
from shared.domain.contract import Action, AgentName
from shared.domain.ports.clock import Clock


class StrategistAgent:
    """Agente Estratega de venta: recomienda vender ahora, esperar o «sin señal clara»."""

    name = AgentName.STRATEGIST

    def __init__(
        self, get_selling_advice: GetSellingAdvice, clock: Clock, hit_rate: float | None = None
    ) -> None:
        self._get_selling_advice = get_selling_advice
        self._clock = clock
        self._hit_rate = hit_rate  # acierto de la regla en la prueba retrospectiva

    def handle(self, message: AgentMessage) -> AgentMessage:
        now = self._clock.now()
        if message.action != Action.GET_SELLING_ADVICE:
            return message.reply_failure(f"Acción no soportada: {message.action}", now)
        return message.reply_inform(self._to_dict(self._get_selling_advice.execute()), now)

    def _to_dict(self, advice: SellingAdvice) -> dict[str, Any]:
        return {
            "verdict": advice.verdict.value,
            "reason": advice.reason,
            "current_soles": float(advice.current_price) if advice.current_price else None,
            "target_date": advice.target_day.isoformat() if advice.target_day else None,
            "target_soles": float(advice.target_price) if advice.target_price else None,
            "change_pct": float(advice.change_pct) if advice.change_pct is not None else None,
            "hit_rate_pct": self._hit_rate,
            "disclaimer": DISCLAIMER,
            "sources": ["Bolsa de Nueva York (ICE)", "Pronóstico del Agente Predictor"],
        }
