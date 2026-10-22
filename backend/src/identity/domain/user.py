from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

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

    @classmethod
    def create(
        cls, phone: PhoneNumber, password_hash: str, consent: Consent, at: datetime
    ) -> "User":
        return cls(str(uuid4()), phone, password_hash, consent, at)

    @classmethod
    def create_admin(cls, phone: PhoneNumber, password_hash: str, at: datetime) -> "User":
        """Los administradores se crean por script, sin código de invitación."""
        return cls(str(uuid4()), phone, password_hash, Consent(TEAM_CONSENT, at), at, Role.ADMIN)
