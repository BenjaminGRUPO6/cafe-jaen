"""Mensaje estándar entre agentes.

Todos los agentes se comunican solo con AgentMessage y siempre a través del
Agente Supervisor. Así los módulos no dependen unos de otros.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class Performative(StrEnum):
    """Intención comunicativa del mensaje (inspirada en FIPA-ACL)."""

    REQUEST = "REQUEST"  # pide que se ejecute una acción
    INFORM = "INFORM"  # entrega el resultado de una acción
    FAILURE = "FAILURE"  # comunica un error controlado


@dataclass(frozen=True)
class AgentMessage:
    """Mensaje inmutable que viaja entre el supervisor y los agentes."""

    sender: str
    receiver: str
    performative: Performative
    action: str
    content: dict[str, Any]
    sent_at: datetime
    conversation_id: UUID = field(default_factory=uuid4)
    id: UUID = field(default_factory=uuid4)

    @classmethod
    def request(
        cls,
        sender: str,
        receiver: str,
        action: str,
        content: dict[str, Any],
        sent_at: datetime,
    ) -> AgentMessage:
        """Crea una solicitud nueva (inicia una conversación)."""
        return cls(sender, receiver, Performative.REQUEST, action, content, sent_at)

    def reply_inform(self, content: dict[str, Any], sent_at: datetime) -> AgentMessage:
        """Responde con un resultado; invierte emisor y receptor y conserva la conversación."""
        return self._reply(Performative.INFORM, content, sent_at)

    def reply_failure(self, reason: str, sent_at: datetime) -> AgentMessage:
        """Responde con un error controlado que el emisor puede manejar."""
        return self._reply(Performative.FAILURE, {"reason": reason}, sent_at)

    @property
    def is_failure(self) -> bool:
        return self.performative is Performative.FAILURE

    def _reply(
        self, performative: Performative, content: dict[str, Any], sent_at: datetime
    ) -> AgentMessage:
        return replace(
            self,
            sender=self.receiver,
            receiver=self.sender,
            performative=performative,
            content=content,
            sent_at=sent_at,
            id=uuid4(),
        )
