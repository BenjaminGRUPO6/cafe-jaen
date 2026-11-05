from dataclasses import dataclass

from shared.domain.ports.clock import Clock
from support.domain.ports import SupportRepository
from support.domain.support_message import Author, SupportMessage, ThreadSummary


@dataclass(frozen=True)
class Conversation:
    messages: list[SupportMessage]


class FarmerSupport:
    """El caficultor escribe sus dudas al equipo y lee las respuestas."""

    def __init__(self, repository: SupportRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    def write(self, user_id: str, text: str) -> SupportMessage:
        message = SupportMessage.write(user_id, Author.FARMER, text, self._clock.now())
        return self._repository.add(message)

    def conversation(self, user_id: str) -> Conversation:
        """Al abrirla, las respuestas del equipo quedan como leídas."""
        self._repository.mark_read(user_id, written_by=Author.TEAM)
        return Conversation(self._repository.thread(user_id))

    def unread_replies(self, user_id: str) -> int:
        return self._repository.unread(user_id, written_by=Author.TEAM)


class TeamSupport:
    """El equipo revisa la bandeja de «Atención» y responde a cada caficultor."""

    def __init__(self, repository: SupportRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    def inbox(self) -> list[ThreadSummary]:
        return self._repository.threads()

    def conversation(self, user_id: str) -> Conversation:
        """Al abrirla, las preguntas del caficultor quedan como leídas."""
        self._repository.mark_read(user_id, written_by=Author.FARMER)
        return Conversation(self._repository.thread(user_id))

    def reply(self, user_id: str, text: str) -> SupportMessage:
        message = SupportMessage.write(user_id, Author.TEAM, text, self._clock.now())
        return self._repository.add(message)
