from collections.abc import Callable

from identity.domain.errors import (
    AlreadyVerifiedError,
    InvalidVerificationCodeError,
    ResendTooSoonError,
    UserNotFoundError,
    VerificationExpiredError,
)
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.email_sender import EmailNotSentError, EmailSender
from identity.domain.ports.security import TokenIssuer
from identity.domain.ports.user_repository import UserRepository, VerificationRepository
from identity.domain.user import User
from identity.domain.verification import LIFETIME, new_verification
from shared.domain.ports.clock import Clock

SUBJECT = "Tu código para Café Jaén"


class SendVerificationCode:
    """Genera un código nuevo y lo envía al correo del usuario.

    Si el correo no sale (proveedor sin configurar o caído), el código igual queda guardado y
    el equipo lo ve en «Participantes»: la cuenta nunca se queda bloqueada.
    """

    def __init__(
        self,
        users: UserRepository,
        verifications: VerificationRepository,
        sender: EmailSender,
        clock: Clock,
        choice: Callable[[str], str],
    ) -> None:
        self._users = users
        self._verifications = verifications
        self._sender = sender
        self._clock = clock
        self._choice = choice

    def for_new_user(self, user: User) -> bool:
        """Primer envío, justo después del registro. Devuelve si el correo salió."""
        return self._send(user)

    def resend(self, phone: str) -> tuple[User, bool]:
        """Reenvío pedido desde la pantalla «Verificar» (una vez por minuto)."""
        user = self._users.get_by_phone(PhoneNumber(phone))
        if user is None:
            raise UserNotFoundError()
        if user.is_verified:
            raise AlreadyVerifiedError()
        current = self._verifications.get(user.id)
        if current is not None and not current.can_resend(self._clock.now()):
            raise ResendTooSoonError()
        return user, self._send(user)

    def _send(self, user: User) -> bool:
        verification = new_verification(user.id, self._clock.now(), self._choice)
        sent = False
        if user.email is not None:
            try:
                self._sender.send(user.email.value, SUBJECT, _message(verification.code))
                sent = True
            except EmailNotSentError:
                sent = False
        self._verifications.save(verification.with_delivery(sent))
        return sent


class VerifyAccount:
    """Confirma el código: la cuenta queda verificada y se abre la sesión."""

    def __init__(
        self,
        users: UserRepository,
        verifications: VerificationRepository,
        tokens: TokenIssuer,
        clock: Clock,
    ) -> None:
        self._users = users
        self._verifications = verifications
        self._tokens = tokens
        self._clock = clock

    def execute(self, phone: str, code: str) -> str:
        user = self._users.get_by_phone(PhoneNumber(phone))
        if user is None:
            raise UserNotFoundError()
        if user.is_verified:
            raise AlreadyVerifiedError()
        verification = self._verifications.get(user.id)
        if verification is None:
            raise VerificationExpiredError()
        now = self._clock.now()
        try:
            verification.check(code, now)
        except InvalidVerificationCodeError:
            self._verifications.save(verification.failed())
            raise
        self._users.mark_verified(user.id, now)
        self._verifications.delete(user.id)
        self._users.record_login(user.id, now)
        return self._tokens.issue(user.id, user.role)


def _message(code: str) -> str:
    minutes = int(LIFETIME.total_seconds() // 60)
    return (
        f"Hola:\n\nTu código para activar tu cuenta en Café Jaén es: {code}\n\n"
        f"Escríbelo en la aplicación. Vence en {minutes} minutos.\n"
        "Si no creaste esta cuenta, ignora este correo.\n\n"
        "Equipo Café Jaén — Universidad Privada Antenor Orrego"
    )
