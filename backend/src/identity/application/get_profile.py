from identity.domain.errors import UserNotFoundError
from identity.domain.ports.user_repository import UserRepository
from identity.domain.user import User


class GetProfile:
    """Datos de la cuenta que inició sesión: la cabecera muestra su nombre y su rol."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: str) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
