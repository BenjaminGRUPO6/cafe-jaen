from typing import Protocol

from support.domain.support_message import Author, SupportMessage, ThreadSummary


class SupportRepository(Protocol):
    def add(self, message: SupportMessage) -> SupportMessage: ...

    def thread(self, user_id: str) -> list[SupportMessage]:
        """Mensajes de una conversación, del más antiguo al más reciente."""
        ...

    def threads(self) -> list[ThreadSummary]:
        """Una fila por conversación: primero las que tienen mensajes sin leer."""
        ...

    def mark_read(self, user_id: str, written_by: Author) -> None:
        """Marca como leídos los mensajes de `written_by` en esa conversación."""
        ...

    def unread(self, user_id: str, written_by: Author) -> int: ...
