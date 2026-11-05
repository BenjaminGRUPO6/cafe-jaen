from collections.abc import Callable

from identity.domain.errors import IdentityError
from identity.domain.invitation_code import InvitationCode, new_invitation_code
from identity.domain.ports.user_repository import InvitationCodeRepository
from identity.domain.user import Role

MAX_CODES_PER_REQUEST = 50


class InvalidCodeCountError(IdentityError):
    def __init__(self) -> None:
        super().__init__(f"Se pueden generar entre 1 y {MAX_CODES_PER_REQUEST} códigos a la vez")


class CodeNotFoundError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Ese código no existe")


class UsedCodeError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Ese código ya fue usado por un participante: no se puede borrar")


class ManageInvitationCodes:
    """El equipo genera y revisa los códigos del GE desde la app (sin terminal en Render)."""

    def __init__(self, codes: InvitationCodeRepository, choice: Callable[[str], str]) -> None:
        self._codes = codes
        self._choice = choice  # secrets.choice en producción; determinista en las pruebas

    def generate(self, count: int, role: Role = Role.FARMER) -> list[str]:
        """Códigos para caficultores o, con `Role.ADMIN`, para más cuentas del equipo."""
        if not 1 <= count <= MAX_CODES_PER_REQUEST:
            raise InvalidCodeCountError()
        existing = {c.code for c in self._codes.all()}
        created: list[str] = []
        while len(created) < count:
            code = new_invitation_code(self._choice, role)
            if code not in existing:  # un código repetido daría acceso doble
                existing.add(code)
                created.append(code)
        self._codes.add_many(created, role)
        return created

    def list(self) -> list[InvitationCode]:
        return self._codes.all()

    def delete(self, code: str) -> None:
        """Solo códigos sin usar: uno usado identifica a un participante y no se borra."""
        current = self._codes.get(code)
        if current is None:
            raise CodeNotFoundError()
        if current.is_used:
            raise UsedCodeError()
        self._codes.delete(code)
