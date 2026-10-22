from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from shared.domain.agent_message import Performative


@dataclass(frozen=True)
class AgentTrace:
    """Registro de una interacción entre agentes (HU07, RNF08)."""

    conversation_id: UUID
    sender: str
    receiver: str
    action: str
    result: Performative
    duration_ms: int
    recorded_at: datetime
    detail: str | None = None  # motivo, si el resultado fue FAILURE
