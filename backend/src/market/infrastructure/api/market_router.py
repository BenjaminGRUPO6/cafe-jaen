import asyncio
import json
from collections.abc import AsyncIterator, Callable
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from shared.domain.contract import Action, AgentName
from shared.domain.ports.agent_gateway import AgentGateway
from shared.infrastructure.api.responses import unwrap

HEARTBEAT_SECONDS = 15  # mantiene viva la conexión en redes móviles


class HistoryPeriod(StrEnum):
    """Periodos del gráfico tipo bolsa (HU04)."""

    TODAY = "today"
    LAST_30_DAYS = "30"
    LAST_90_DAYS = "90"


class LocalPriceRequest(BaseModel):
    """Precio que una cooperativa paga hoy al productor (HU12)."""

    cooperative: str = Field(min_length=1, max_length=80)
    coffee_type: str = Field(description="convencional, organico o especial")
    paid_soles: float = Field(gt=0, description="S/ por quintal")


def build_market_router(
    gateway: AgentGateway,
    require_user: Callable[..., str],
    require_admin: Callable[..., str],
    latest_quote_time: Callable[[], datetime | None],
    poll_seconds: float = 5.0,
    max_events: int | None = None,
) -> APIRouter:
    """Rutas del precio mundial: todas pasan por el supervisor hacia el Agente Analista.

    `latest_quote_time` es una consulta liviana para saber si llegó un precio nuevo sin
    molestar a los agentes en cada vuelta; `max_events` solo se usa en las pruebas.
    """
    router = APIRouter(tags=["market"], dependencies=[Depends(require_user)])

    def ask_analyst(action: Action, content: dict[str, Any] | None = None) -> dict[str, Any]:
        return unwrap(gateway.request(AgentName.API, AgentName.ANALYST, action, content))

    @router.get("/prices/live")
    def live_price() -> dict[str, Any]:
        return ask_analyst(Action.GET_LIVE_PRICE)

    @router.get("/prices/history")
    def price_history(
        period: Annotated[HistoryPeriod, Query()] = HistoryPeriod.LAST_30_DAYS,
    ) -> dict[str, Any]:
        return ask_analyst(Action.GET_PRICE_HISTORY, {"period": period.value})

    @router.post(
        "/admin/local-prices",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_admin)],
    )
    def record_local_price(body: LocalPriceRequest) -> dict[str, Any]:
        reply = gateway.request(
            AgentName.API, AgentName.ANALYST, Action.RECORD_LOCAL_PRICE, body.model_dump()
        )
        if reply.is_failure:
            # Los errores de validación se muestran tal cual al equipo para que corrija el dato
            raise HTTPException(status.HTTP_400_BAD_REQUEST, reply.content["reason"])
        return reply.content

    @router.get("/admin/local-prices", dependencies=[Depends(require_admin)])
    def local_prices() -> dict[str, Any]:
        return ask_analyst(Action.GET_LOCAL_PRICES)

    @router.get("/prices/stream")
    async def price_stream(request: Request) -> StreamingResponse:
        """Server-Sent Events: envía el precio en vivo cada vez que llega una cotización nueva."""

        async def events() -> AsyncIterator[str]:
            sent, last_seen, idle = 0, object(), 0.0
            while max_events is None or sent < max_events:
                if await request.is_disconnected():
                    break
                current = await run_in_threadpool(latest_quote_time)
                if current != last_seen:
                    reply = await run_in_threadpool(
                        gateway.request, AgentName.API, AgentName.ANALYST, Action.GET_LIVE_PRICE
                    )
                    if not reply.is_failure:
                        yield f"event: price\ndata: {json.dumps(reply.content)}\n\n"
                        sent += 1
                    last_seen, idle = current, 0.0
                    continue
                await asyncio.sleep(poll_seconds)
                idle += poll_seconds
                if idle >= HEARTBEAT_SECONDS:
                    yield ": ping\n\n"
                    idle = 0.0

        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        return StreamingResponse(events(), media_type="text/event-stream", headers=headers)

    return router
