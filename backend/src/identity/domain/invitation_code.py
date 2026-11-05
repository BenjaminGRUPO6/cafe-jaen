from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime

from identity.domain.errors import InvalidInvitationCodeError
from identity.domain.user import Role


@dataclass(frozen=True)
class InvitationCode:
    """Código entregado solo al grupo experimental; se puede usar una única vez.

    Así se garantiza que el grupo de control no acceda a la aplicación.
    """

    code: str
    used_by: str | None = None
    used_at: datetime | None = None
    role: Role = Role.FARMER  # con un código del equipo se crea una cuenta de administrador

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
TEAM_CODE_PREFIX = "EQUIPO-"
CODE_LENGTH = 6


def new_invitation_code(choice: Callable[[str], str], role: Role = Role.FARMER) -> str:
    """«JAEN-7KQ2MX» para caficultores y «EQUIPO-7KQ2MX» para el equipo.

    `choice` elige un carácter (secrets.choice en producción).
    """
    prefix = TEAM_CODE_PREFIX if role is Role.ADMIN else CODE_PREFIX
    return prefix + "".join(choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
