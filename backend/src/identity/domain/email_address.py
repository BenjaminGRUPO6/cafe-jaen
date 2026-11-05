import re
from dataclasses import dataclass

from identity.domain.errors import InvalidEmailError

# Validación sencilla: algo@dominio.ext (la verificación real es el código que llega al correo)
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$")
MAX_LENGTH = 120


@dataclass(frozen=True)
class EmailAddress:
    """Correo del usuario (objeto de valor), siempre en minúsculas y sin espacios."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if len(normalized) > MAX_LENGTH or not _EMAIL.match(normalized):
            raise InvalidEmailError()
        object.__setattr__(self, "value", normalized)

    def masked(self) -> str:
        """«lu***@gmail.com»: para decir a dónde se envió el código sin mostrarlo completo."""
        local, domain = self.value.split("@", 1)
        return f"{local[:2]}***@{domain}"
