from identity.domain.errors import (
    AccountNotVerifiedError,
    IdentityError,
    InvalidCredentialsError,
)
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.security import PasswordHasher, TokenIssuer
from identity.domain.ports.user_repository import UserRepository
from shared.domain.ports.clock import Clock


class AuthenticateUser:
    """HU01: inicia sesión y devuelve un token válido por 30 días."""

    def __init__(
        self, users: UserRepository, hasher: PasswordHasher, tokens: TokenIssuer, clock: Clock
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._clock = clock

    def execute(self, phone: str, password: str) -> str:
        try:
            user = self._users.get_by_phone(PhoneNumber(phone))
        except IdentityError:
            # No se revela si el problema fue el celular o la contraseña
            raise InvalidCredentialsError() from None
        if user is None or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()
        # Solo después de comprobar la contraseña: así no se revela qué cuentas existen
        if not user.is_verified:
            raise AccountNotVerifiedError()
        # El equipo ve en «Participantes» cuándo entró cada caficultor por última vez
        self._users.record_login(user.id, self._clock.now())
        return self._tokens.issue(user.id, user.role)
