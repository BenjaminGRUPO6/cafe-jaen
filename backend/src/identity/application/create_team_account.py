from dataclasses import dataclass

from identity.domain.errors import PhoneAlreadyRegisteredError, WeakPasswordError
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.security import PasswordHasher
from identity.domain.ports.user_repository import UserRepository
from identity.domain.user import User, clean_name
from shared.domain.ports.clock import Clock

MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class TeamAccountCommand:
    name: str
    phone: str
    password: str


class CreateTeamAccount:
    """Un administrador crea otra cuenta del equipo con su celular y contraseña.

    Queda activa de inmediato (sin código de invitación ni verificación): quien la crea ya es
    del equipo y le entrega los datos en persona.
    """

    def __init__(self, users: UserRepository, hasher: PasswordHasher, clock: Clock) -> None:
        self._users = users
        self._hasher = hasher
        self._clock = clock

    def execute(self, command: TeamAccountCommand) -> User:
        if len(command.password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(MIN_PASSWORD_LENGTH)
        phone = PhoneNumber(command.phone.strip())
        if self._users.get_by_phone(phone) is not None:
            raise PhoneAlreadyRegisteredError()
        account = User.create_admin(
            phone, self._hasher.hash(command.password), self._clock.now(), clean_name(command.name)
        )
        self._users.add(account, None)
        return account
