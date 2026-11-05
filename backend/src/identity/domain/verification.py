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
class EmailVerification:
    """Código de 6 dígitos que confirma que el correo (y la persona) existen.

    Vence a los 15 minutos y admite 5 intentos; el equipo también lo ve en «Participantes»
    por si el correo no llega (se lo envía al caficultor por WhatsApp).
    """

    user_id: str
    code: str
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    email_sent: bool = False

    def check(self, code: str, now: datetime) -> "EmailVerification":
        """Devuelve la verificación con un intento más si el código no coincide."""
        if self.attempts >= MAX_ATTEMPTS:
            raise TooManyAttemptsError()
        if now > self.expires_at:
            raise VerificationExpiredError()
        if code.strip() != self.code:
            raise InvalidVerificationCodeError(MAX_ATTEMPTS - self.attempts - 1)
        return self

    def failed(self) -> "EmailVerification":
        return replace(self, attempts=self.attempts + 1)

    def can_resend(self, now: datetime) -> bool:
        return now - self.created_at >= RESEND_AFTER

    def with_delivery(self, sent: bool) -> "EmailVerification":
        return replace(self, email_sent=sent)


def new_verification(
    user_id: str, now: datetime, choice: Callable[[str], str]
) -> EmailVerification:
    """`choice` elige cada dígito (secrets.choice en producción; determinista en las pruebas)."""
    code = "".join(choice("0123456789") for _ in range(CODE_DIGITS))
    return EmailVerification(user_id, code, now, now + LIFETIME)
