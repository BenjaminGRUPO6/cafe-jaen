from typing import Protocol

from identity.domain.invitation_code import InvitationCode
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User


class UserRepository(Protocol):
    def get_by_phone(self, phone: PhoneNumber) -> User | None: ...

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        """Guarda el usuario y marca el código como usado en una sola transacción.

        Los administradores no usan código (`redeemed_code=None`).
        """
        ...


class InvitationCodeRepository(Protocol):
    def get(self, code: str) -> InvitationCode | None: ...
