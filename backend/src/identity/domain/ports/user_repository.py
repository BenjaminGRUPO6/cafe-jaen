from datetime import datetime
from typing import Protocol

from identity.domain.email_address import EmailAddress
from identity.domain.invitation_code import InvitationCode
from identity.domain.participant import CodeSummary, Participant
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import Role, User
from identity.domain.verification import EmailVerification


class UserRepository(Protocol):
    def get_by_phone(self, phone: PhoneNumber) -> User | None: ...

    def get_by_id(self, user_id: str) -> User | None: ...

    def get_by_email(self, email: EmailAddress) -> User | None: ...

    def mark_verified(self, user_id: str, at: datetime) -> None: ...

    def delete(self, user_id: str) -> None:
        """Borra la cuenta, su verificación pendiente y libera su código de invitación."""
        ...

    def count_admins(self) -> int: ...

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        """Guarda el usuario y marca el código como usado en una sola transacción.

        Los administradores no usan código (`redeemed_code=None`).
        """
        ...

    def record_login(self, user_id: str, at: datetime) -> None: ...

    def participants(self) -> list[Participant]:
        """Todos los usuarios, del registro más reciente al más antiguo."""
        ...


class VerificationRepository(Protocol):
    def save(self, verification: EmailVerification) -> None:
        """Guarda o reemplaza la verificación pendiente del usuario."""
        ...

    def get(self, user_id: str) -> EmailVerification | None: ...

    def delete(self, user_id: str) -> None: ...

    def pending(self) -> dict[str, EmailVerification]:
        """Verificaciones pendientes por id de usuario (pantalla «Participantes»)."""
        ...


class InvitationCodeRepository(Protocol):
    def get(self, code: str) -> InvitationCode | None: ...

    def summary(self) -> CodeSummary: ...

    def all(self) -> list[InvitationCode]:
        """Todos los códigos: primero los libres, luego los usados (del más reciente)."""
        ...

    def add_many(self, codes: list[str], role: Role = Role.FARMER) -> None: ...

    def delete(self, code: str) -> None: ...
