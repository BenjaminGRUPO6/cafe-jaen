from datetime import date
from decimal import Decimal
from typing import Any

from decision.domain.selling_decision import (
    ForecastDay,
    MarketSnapshot,
    SellingAdvice,
    SellingDecision,
    Verdict,
)
from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway
from shared.domain.ports.clock import Clock


class GetSellingAdvice:
    """HU05: pide el precio en vivo y el pronóstico a otros agentes y aplica la regla."""

    def __init__(self, gateway: AgentGateway, decision: SellingDecision, clock: Clock) -> None:
        self._gateway = gateway
        self._decision = decision
        self._clock = clock

    def execute(self) -> SellingAdvice:
        # El Estratega no conoce a los otros módulos: pide los datos al supervisor
        price = self._ask(AgentName.ANALYST, Action.GET_LIVE_PRICE)
        if price is None:
            return SellingAdvice(Verdict.NO_DATA, "No hay precio de la bolsa disponible.")
        forecast = self._ask(AgentName.FORECASTER, Action.GET_FORECAST) or {}
        snapshot = MarketSnapshot(
            current_price=Decimal(str(price["price_soles"])),
            priced_at=price["quoted_at"],
            price_is_stale=bool(price.get("stale", False)),
            forecast=[_forecast_day(point) for point in forecast.get("points", [])],
            forecast_generated_on=(
                date.fromisoformat(forecast["generated_on"]) if "generated_on" in forecast else None
            ),
        )
        return self._decision.decide(snapshot, self._clock.today())

    def _ask(self, receiver: AgentName, action: Action) -> dict[str, Any] | None:
        reply = self._gateway.request(AgentName.STRATEGIST, receiver, action)
        return None if reply.is_failure else reply.content


def _forecast_day(point: dict[str, Any]) -> ForecastDay:
    return ForecastDay(
        day=date.fromisoformat(point["date"]),
        expected=Decimal(str(point["expected_soles"])),
        lower=Decimal(str(point["lower_soles"])),
        upper=Decimal(str(point["upper_soles"])),
    )
