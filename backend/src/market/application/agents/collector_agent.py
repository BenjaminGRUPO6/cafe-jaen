from dataclasses import asdict

from market.application.collect_prices import CollectPrices
from shared.domain.agent_message import AgentMessage
from shared.domain.contract import Action, AgentName
from shared.domain.ports.clock import Clock


class CollectorAgent:
    """Agente Recolector: mantiene al día el precio mundial consultando varias webs."""

    name = AgentName.COLLECTOR

    def __init__(self, collect_prices: CollectPrices, clock: Clock) -> None:
        self._collect_prices = collect_prices
        self._clock = clock

    def handle(self, message: AgentMessage) -> AgentMessage:
        now = self._clock.now()
        if message.action != Action.COLLECT_PRICES:
            return message.reply_failure(f"Acción no soportada: {message.action}", now)
        report = self._collect_prices.execute(force=bool(message.content.get("force", False)))
        return message.reply_inform(asdict(report), now)
