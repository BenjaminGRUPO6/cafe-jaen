from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from identity.domain.invitation_code import InvitationCode
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import Consent, Role, User
from identity.infrastructure.persistence.tables import invitation_codes, users


class SqlAlchemyUserRepository:
    """Implementa UserRepository sobre PostgreSQL (o SQLite en pruebas)."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def get_by_phone(self, phone: PhoneNumber) -> User | None:
        with self._sessions() as session:
            row = session.execute(select(users).where(users.c.phone == phone.value)).first()
        if row is None:
            return None
        return User(
            id=row.id,
            phone=PhoneNumber(row.phone),
            password_hash=row.password_hash,
            consent=Consent(row.consent_version, row.consent_accepted_at),
            created_at=row.created_at,
            role=Role(row.role),
        )

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        # session.begin() confirma ambas operaciones o ninguna
        with self._sessions() as session, session.begin():
            session.execute(
                insert(users).values(
                    id=user.id,
                    phone=user.phone.value,
                    password_hash=user.password_hash,
                    consent_version=user.consent.version,
                    consent_accepted_at=user.consent.accepted_at,
                    created_at=user.created_at,
                    role=user.role.value,
                )
            )
            if redeemed_code is None:
                return  # administrador: no usa código de invitación
            session.execute(
                update(invitation_codes)
                .where(invitation_codes.c.code == redeemed_code.code)
                .values(used_by=redeemed_code.used_by, used_at=redeemed_code.used_at)
            )


class SqlAlchemyInvitationCodeRepository:
    """Implementa InvitationCodeRepository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def get(self, code: str) -> InvitationCode | None:
        with self._sessions() as session:
            row = session.execute(
                select(invitation_codes).where(invitation_codes.c.code == code)
            ).first()
        return InvitationCode(row.code, row.used_by, row.used_at) if row else None

    def add_many(self, codes: list[str]) -> None:
        """Usado por el script que genera los códigos del GE."""
        with self._sessions() as session, session.begin():
            session.execute(insert(invitation_codes), [{"code": c} for c in codes])
