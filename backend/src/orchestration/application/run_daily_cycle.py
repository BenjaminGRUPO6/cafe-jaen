from dataclasses import dataclass
from typing import Any

from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway


@dataclass(frozen=True)
class DailyCycleReport:
    collection: dict[str, Any]
    forecast_generated: bool
    detail: str | None = None


class CollectLivePrices:
    """Disparo de cada minuto: el Recolector decide si la bolsa está abierta (HU02)."""

    def __init__(self, gateway: AgentGateway) -> None:
        self._gateway = gateway

    def execute(self) -> dict[str, Any]:
        reply = self._gateway.request(
            AgentName.SCHEDULER, AgentName.COLLECTOR, Action.COLLECT_PRICES
        )
        return reply.content


class RunDailyCycle:
    """Ciclo autónomo después del cierre de la bolsa (Figura 4 de la arquitectura).

    Recolector (cierre) → Analista (histórico) → Predictor. Los agentes no se conocen:
    el supervisor les pasa los datos de uno a otro.
    """

    def __init__(self, gateway: AgentGateway, history_days: int) -> None:
        self._gateway = gateway
        self._history_days = history_days

    def execute(self) -> DailyCycleReport:
        # force: con la bolsa ya cerrada se consulta una vez más para guardar el cierre
        collection = self._ask(AgentName.COLLECTOR, Action.COLLECT_PRICES, {"force": True})
        history = self._ask(
            AgentName.ANALYST, Action.GET_PRICE_HISTORY, {"period": str(self._history_days)}
        )
        if "reason" in history:
            return DailyCycleReport(collection, forecast_generated=False, detail=history["reason"])
        forecast = self._ask(
            AgentName.FORECASTER, Action.GENERATE_FORECAST, {"points": history["points"]}
        )
        return DailyCycleReport(collection, "reason" not in forecast, forecast.get("reason"))

    def _ask(
        self, receiver: AgentName, action: Action, content: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self._gateway.request(AgentName.SCHEDULER, receiver, action, content).content
