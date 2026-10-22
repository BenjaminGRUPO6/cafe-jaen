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
