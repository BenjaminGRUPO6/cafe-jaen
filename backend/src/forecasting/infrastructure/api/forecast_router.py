from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends

from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway
from shared.infrastructure.api.responses import unwrap


def build_forecast_router(gateway: AgentGateway, require_user: Callable[..., str]) -> APIRouter:
    router = APIRouter(tags=["forecast"], dependencies=[Depends(require_user)])

    @router.get("/forecast")
    def latest_forecast() -> dict[str, Any]:
        return unwrap(gateway.request(AgentName.API, AgentName.FORECASTER, Action.GET_FORECAST))

    return router
