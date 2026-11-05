from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from support.domain.errors import EmptyMessageError, MessageTooLongError

MAX_LENGTH = 1000


class Author(StrEnum):
    FARMER = "farmer"  # el caficultor pregunta
    TEAM = "team"  # el equipo responde


@dataclass(frozen=True)
class SupportMessage:
    """Un mensaje de «Atención»: la conversación de cada caficultor con el equipo."""

    user_id: str  # el caficultor dueño de la conversación (también en las respuestas)
    author: Author
    text: str
    created_at: datetime
    read: bool = False  # lo leyó la otra parte
    id: int | None = None

    @classmethod
    def write(cls, user_id: str, author: Author, text: str, at: datetime) -> "SupportMessage":
        clean = text.strip()
        if not clean:
            raise EmptyMessageError()
        if len(clean) > MAX_LENGTH:
            raise MessageTooLongError(MAX_LENGTH)
        return cls(user_id, author, clean, at)


@dataclass(frozen=True)
class ThreadSummary:
    """Fila de la bandeja del equipo: una conversación y cuántos mensajes faltan leer."""

    user_id: str
    last_text: str
    last_at: datetime
    last_author: Author
    unread: int  # mensajes del caficultor que el equipo aún no abrió
