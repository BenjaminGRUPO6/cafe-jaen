from dataclasses import dataclass
from datetime import datetime

from identity.domain.user import Role


@dataclass(frozen=True)
class Participant:
    """Fila de la pantalla «Participantes»: quién se registró, con qué código y cuándo entró."""

    phone: str
    role: Role
    registered_at: datetime
    invitation_code: str | None  # None para el equipo (se crea sin código)
    last_login_at: datetime | None  # None si nunca volvió a iniciar sesión


@dataclass(frozen=True)
class CodeSummary:
    total: int
    used: int
