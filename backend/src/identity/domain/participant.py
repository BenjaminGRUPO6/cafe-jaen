from dataclasses import dataclass
from datetime import datetime

from identity.domain.user import Role


@dataclass(frozen=True)
class Participant:
    """Fila de la pantalla «Participantes»: quién se registró, con qué código y cuándo entró."""

    user_id: str
    phone: str
    role: Role
    registered_at: datetime
    invitation_code: str | None  # None para el equipo (se crea sin código)
    last_login_at: datetime | None  # None si nunca volvió a iniciar sesión
    email: str | None = None
    verified: bool = True
    pending_code: str | None = None  # código por verificar (el equipo lo envía si no llega)
    code_emailed: bool = False  # si el correo con el código se pudo enviar


@dataclass(frozen=True)
class CodeSummary:
    total: int
    used: int
