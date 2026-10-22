from typing import Protocol


class TokenVerifier(Protocol):
    """Valida un token de sesión y devuelve el id del usuario, o None si no es válido."""

    def verify(self, token: str) -> str | None: ...

    def role(self, token: str) -> str | None:
        """Rol guardado en el token («farmer» o «admin»), o None si no es válido."""
        ...
