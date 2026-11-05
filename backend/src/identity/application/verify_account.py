from collections.abc import Callable, Sequence

from identity.domain.errors import (
    AlreadyVerifiedError,
    InvalidVerificationCodeError,
    ResendTooSoonError,
    UserNotFoundError,
    VerificationExpiredError,
)
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.code_sender import CodeNotSentError, CodeSender
from identity.domain.ports.security import TokenIssuer
from identity.domain.ports.user_repository import UserRepository, VerificationRepository
from identity.domain.user import User
from identity.domain.verification import new_verification
from shared.domain.ports.clock import Clock


class SendVerificationCode:
    """Genera un código nuevo y lo entrega por el primer canal que funcione.

    Prioridad: WhatsApp al celular y, si no se puede, el correo (si lo dio). Si ningún canal
    funciona, el código igual queda guardado y el equipo lo ve en «Participantes» para
    enviarlo a mano: la cuenta nunca se queda bloqueada.
    """

    def __init__(
        self,
        users: UserRepository,
        verifications: VerificationRepository,
        senders: Sequence[CodeSender],
        clock: Clock,
        choice: Callable[[str], str],
    ) -> None:
        self._users = users
        self._verifications = verifications
        self._senders = senders  # en orden de prioridad
        self._clock = clock
        self._choice = choice

    def for_new_user(self, user: User) -> str | None:
        """Primer envío, justo después del registro. Devuelve el canal usado (o None)."""
        return self._send(user)

    def resend(self, phone: str) -> tuple[User, str | None]:
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

    def _send(self, user: User) -> str | None:
        verification = new_verification(user.id, self._clock.now(), self._choice)
        channel = None
        for sender in self._senders:
            try:
                sender.send(user, verification.code)
            except CodeNotSentError:
                continue
            channel = sender.channel
            break
        self._verifications.save(verification.delivered(channel))
        return channel


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
