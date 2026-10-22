from typing import Any

from fastapi import HTTPException, status

from shared.domain.agent_message import AgentMessage


def unwrap(reply: AgentMessage) -> dict[str, Any]:
    """Convierte la respuesta de un agente en el cuerpo HTTP o en un error claro."""
    if reply.is_failure:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No pudimos obtener la información en este momento. Intenta en unos minutos.",
        )
    return reply.content
