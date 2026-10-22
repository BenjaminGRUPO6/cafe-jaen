from typing import Any, Protocol

from shared.domain.agent_message import AgentMessage


class AgentGateway(Protocol):
    """Puerto para pedir algo a un agente sin conocerlo: lo implementa el supervisor."""

    def request(
        self, sender: str, receiver: str, action: str, content: dict[str, Any] | None = None
    ) -> AgentMessage: ...
