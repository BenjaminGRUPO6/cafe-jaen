from identity.domain.errors import CannotDeleteSelfError, LastAdminError, UserNotFoundError
from identity.domain.ports.user_repository import UserRepository
from identity.domain.user import Role


class DeleteParticipant:
    """El equipo elimina una cuenta (por ejemplo, un registro con datos inventados).

    Su código de invitación queda libre otra vez. Nadie puede eliminarse a sí mismo y siempre
    queda al menos una cuenta del equipo.
    """

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: str, requested_by: str) -> None:
        if user_id == requested_by:
            raise CannotDeleteSelfError()
        user = self._users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        if user.role is Role.ADMIN and self._users.count_admins() <= 1:
            raise LastAdminError()
        self._users.delete(user_id)
