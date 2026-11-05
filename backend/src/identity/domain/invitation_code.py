from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime

from identity.domain.errors import InvalidInvitationCodeError


@dataclass(frozen=True)
class InvitationCode:
    """Código entregado solo al grupo experimental; se puede usar una única vez.

    Así se garantiza que el grupo de control no acceda a la aplicación.
    """

    code: str
    used_by: str | None = None
    used_at: datetime | None = None

    @property
    def is_used(self) -> bool:
        return self.used_by is not None

    def redeem(self, user_id: str, at: datetime) -> "InvitationCode":
        if self.is_used:
            raise InvalidInvitationCodeError()
        return replace(self, used_by=user_id, used_at=at)


# Sin letras ni números que se confunden al leerlos o dictarlos (0/O, 1/I/L)
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_PREFIX = "JAEN-"
CODE_LENGTH = 6


def new_invitation_code(choice: Callable[[str], str]) -> str:
    """Código como «JAEN-7KQ2MX». `choice` elige un carácter (secrets.choice en producción)."""
    return CODE_PREFIX + "".join(choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
