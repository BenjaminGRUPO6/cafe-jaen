import time
from typing import Any

from orchestration.domain.ports.agent_router import AgentRouter
from orchestration.domain.ports.trace_repository import TraceRepository
from orchestration.domain.trace import AgentTrace
from shared.domain.agent_message import AgentMessage
from shared.domain.ports.clock import Clock


class DispatchRequest:
    """Agente Supervisor (lógica): recibe cada solicitud, la enruta y registra la traza.

    Implementa el puerto AgentGateway, así que la API, el planificador y el propio
    Agente Asesor piden datos a los agentes sin conocerlos.
    """

    def __init__(self, router: AgentRouter, traces: TraceRepository, clock: Clock) -> None:
        self._router = router
        self._traces = traces
        self._clock = clock

    def request(
        self, sender: str, receiver: str, action: str, content: dict[str, Any] | None = None
    ) -> AgentMessage:
        message = AgentMessage.request(sender, receiver, action, content or {}, self._clock.now())
        started = time.perf_counter()
        reply = self._router.route(message)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        self._traces.add(
            AgentTrace(
                conversation_id=message.conversation_id,
                sender=sender,
                receiver=receiver,
                action=action,
                result=reply.performative,
                duration_ms=elapsed_ms,
                recorded_at=self._clock.now(),
                detail=reply.content.get("reason") if reply.is_failure else None,
            )
        )
        return reply
