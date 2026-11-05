from identity.domain.errors import WeakPasswordError
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.security import PasswordHasher
from identity.domain.ports.user_repository import UserRepository
from identity.domain.user import User
from shared.domain.ports.clock import Clock

MIN_PASSWORD_LENGTH = 8


class EnsureAdmin:
    """Crea la cuenta del equipo si todavía no existe (arranque en Render, sin terminal).

    Es idempotente: si el celular ya está registrado, no cambia nada.
    """

    def __init__(self, users: UserRepository, hasher: PasswordHasher, clock: Clock) -> None:
        self._users = users
        self._hasher = hasher
        self._clock = clock

    def execute(self, phone: str, password: str) -> bool:
        """Devuelve True si creó la cuenta y False si ya existía."""
        number = PhoneNumber(phone)
        if self._users.get_by_phone(number) is not None:
            return False
        if len(password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(MIN_PASSWORD_LENGTH)
        admin = User.create_admin(number, self._hasher.hash(password), self._clock.now())
        self._users.add(admin, None)
        return True
