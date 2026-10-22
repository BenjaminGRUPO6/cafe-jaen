from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway
from shared.infrastructure.api.responses import unwrap


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


def build_advisor_router(gateway: AgentGateway, require_user: Callable[..., str]) -> APIRouter:
    router = APIRouter(prefix="/advisor", tags=["advisor"], dependencies=[Depends(require_user)])

    @router.post("/ask")
    def ask(body: QuestionRequest) -> dict[str, Any]:
        reply = gateway.request(
            AgentName.API, AgentName.ADVISOR, Action.ANSWER_QUESTION, {"question": body.question}
        )
        return unwrap(reply)

    return router
