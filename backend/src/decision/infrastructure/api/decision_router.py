from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends

from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway
from shared.infrastructure.api.responses import unwrap


def build_decision_router(gateway: AgentGateway, require_user: Callable[..., str]) -> APIRouter:
    router = APIRouter(tags=["decision"], dependencies=[Depends(require_user)])

    @router.get("/decision/today")
    def selling_advice() -> dict[str, Any]:
        return unwrap(
            gateway.request(AgentName.API, AgentName.STRATEGIST, Action.GET_SELLING_ADVICE)
        )

    return router
