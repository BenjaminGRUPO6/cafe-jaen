from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from identity.domain.email_address import EmailAddress
from identity.domain.errors import InvalidNameError
from identity.domain.phone_number import PhoneNumber


@dataclass(frozen=True)
class Consent:
    """Aceptación del consentimiento informado (Ley N.° 29733)."""

    version: str
    accepted_at: datetime


TEAM_CONSENT = "equipo"  # los administradores son el equipo de investigación


class Role(StrEnum):
    FARMER = "farmer"  # caficultor del grupo experimental
    ADMIN = "admin"  # equipo: anota los precios que pagan las cooperativas (HU12)


@dataclass(frozen=True)
class User:
    """Usuario de la aplicación: caficultor del GE o administrador del equipo."""

    id: str
    phone: PhoneNumber
    password_hash: str
    consent: Consent
    created_at: datetime
    role: Role = Role.FARMER
    email: EmailAddress | None = None  # None en cuentas anteriores a la verificación por correo
    verified_at: datetime | None = None  # None hasta que confirma el código
    name: str | None = None  # cómo se muestra en la app («Luis Reyes»); opcional

    @property
    def display_name(self) -> str:
        return self.name or self.phone.value

    @property
    def is_verified(self) -> bool:
        return self.verified_at is not None

    @classmethod
    def create(
        cls,
        phone: PhoneNumber,
        password_hash: str,
        consent: Consent,
        at: datetime,
        email: EmailAddress | None = None,
        role: Role = Role.FARMER,
        name: str | None = None,
    ) -> "User":
        """Cuenta nueva desde el registro: queda sin verificar hasta confirmar el código."""
        return cls(str(uuid4()), phone, password_hash, consent, at, role, email, name=name)

    @classmethod
    def create_admin(
        cls, phone: PhoneNumber, password_hash: str, at: datetime, name: str | None = None
    ) -> "User":
        """Cuenta del equipo (al arrancar o creada por otro administrador): ya verificada."""
        return cls(
            str(uuid4()),
            phone,
            password_hash,
            Consent(TEAM_CONSENT, at),
            at,
            Role.ADMIN,
            verified_at=at,
            name=name,
        )


MAX_NAME_LENGTH = 80


def clean_name(name: str) -> str | None:
    """Nombre sin espacios sobrantes; vacío → None. Lanza InvalidNameError si es muy largo."""
    clean = " ".join(name.split())
    if len(clean) > MAX_NAME_LENGTH:
        raise InvalidNameError(MAX_NAME_LENGTH)
    return clean or None
