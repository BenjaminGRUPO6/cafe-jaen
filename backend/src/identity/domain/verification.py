from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from identity.domain.errors import (
    InvalidVerificationCodeError,
    TooManyAttemptsError,
    VerificationExpiredError,
)

CODE_DIGITS = 6
LIFETIME = timedelta(minutes=15)
MAX_ATTEMPTS = 5
RESEND_AFTER = timedelta(seconds=60)


@dataclass(frozen=True)
class Verification:
    """Código de 6 dígitos que confirma que el celular (y la persona) existen.

    Se envía primero por WhatsApp al celular y, si no se puede, al correo. Vence a los
    15 minutos y admite 5 intentos. El equipo también lo ve en «Participantes» por si no llegó.
    """

    user_id: str
    code: str
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    delivered_by: str | None = None  # «whatsapp», «email» o None (solo lo ve el equipo)

    def check(self, code: str, now: datetime) -> "Verification":
        """Comprueba el código; si no coincide, lanza el error con los intentos que quedan."""
        if self.attempts >= MAX_ATTEMPTS:
            raise TooManyAttemptsError()
        if now > self.expires_at:
            raise VerificationExpiredError()
        if code.strip() != self.code:
            raise InvalidVerificationCodeError(MAX_ATTEMPTS - self.attempts - 1)
        return self

    def failed(self) -> "Verification":
        return replace(self, attempts=self.attempts + 1)

    def can_resend(self, now: datetime) -> bool:
        return now - self.created_at >= RESEND_AFTER

    def delivered(self, channel: str | None) -> "Verification":
        return replace(self, delivered_by=channel)


def new_verification(user_id: str, now: datetime, choice: Callable[[str], str]) -> Verification:
    """`choice` elige cada dígito (secrets.choice en producción; determinista en las pruebas)."""
    code = "".join(choice("0123456789") for _ in range(CODE_DIGITS))
    return Verification(user_id, code, now, now + LIFETIME)
