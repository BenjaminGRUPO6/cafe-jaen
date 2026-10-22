import re
from dataclasses import dataclass

from identity.domain.errors import InvalidPhoneError

# Celulares peruanos: 9 dígitos que empiezan con 9
_PERUVIAN_MOBILE = re.compile(r"^9\d{8}$")


@dataclass(frozen=True)
class PhoneNumber:
    """Número de celular validado (objeto de valor)."""

    value: str

    def __post_init__(self) -> None:
        if not _PERUVIAN_MOBILE.match(self.value):
            raise InvalidPhoneError()
