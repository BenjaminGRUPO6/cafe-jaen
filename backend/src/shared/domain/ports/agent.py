from typing import Protocol

from shared.domain.agent_message import AgentMessage


class Agent(Protocol):
    """Puerto común: todo agente recibe un mensaje y devuelve otro."""

    @property
    def name(self) -> str: ...

    def handle(self, message: AgentMessage) -> AgentMessage: ...
