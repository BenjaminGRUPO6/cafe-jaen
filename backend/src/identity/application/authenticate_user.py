from identity.domain.errors import IdentityError, InvalidCredentialsError
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.security import PasswordHasher, TokenIssuer
from identity.domain.ports.user_repository import UserRepository


class AuthenticateUser:
    """HU01: inicia sesión y devuelve un token válido por 30 días."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenIssuer) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    def execute(self, phone: str, password: str) -> str:
        try:
            user = self._users.get_by_phone(PhoneNumber(phone))
        except IdentityError:
            # No se revela si el problema fue el celular o la contraseña
            raise InvalidCredentialsError() from None
        if user is None or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()
        return self._tokens.issue(user.id, user.role)
