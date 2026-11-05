from datetime import datetime
from typing import Protocol

from identity.domain.invitation_code import InvitationCode
from identity.domain.participant import CodeSummary, Participant
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User


class UserRepository(Protocol):
    def get_by_phone(self, phone: PhoneNumber) -> User | None: ...

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        """Guarda el usuario y marca el código como usado en una sola transacción.

        Los administradores no usan código (`redeemed_code=None`).
        """
        ...

    def record_login(self, user_id: str, at: datetime) -> None: ...

    def participants(self) -> list[Participant]:
        """Todos los usuarios, del registro más reciente al más antiguo."""
        ...


class InvitationCodeRepository(Protocol):
    def get(self, code: str) -> InvitationCode | None: ...

    def summary(self) -> CodeSummary: ...

    def all(self) -> list[InvitationCode]:
        """Todos los códigos: primero los libres, luego los usados (del más reciente)."""
        ...

    def add_many(self, codes: list[str]) -> None: ...

    def delete(self, code: str) -> None: ...
