from typing import Protocol

from shared.domain.agent_message import AgentMessage


class AgentRouter(Protocol):
    """Puerto: entrega una solicitud al agente receptor y devuelve su respuesta.

    Nunca lanza excepciones: cualquier error se convierte en un mensaje FAILURE.
    """

    def route(self, message: AgentMessage) -> AgentMessage: ...
