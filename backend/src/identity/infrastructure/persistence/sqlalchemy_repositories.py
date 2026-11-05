from datetime import UTC, datetime

from sqlalchemy import Row, delete, func, insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from identity.domain.email_address import EmailAddress
from identity.domain.invitation_code import InvitationCode
from identity.domain.participant import CodeSummary, Participant
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import Consent, Role, User
from identity.domain.verification import Verification
from identity.infrastructure.persistence.tables import (
    invitation_codes,
    users,
    verification_codes,
)


class SqlAlchemyUserRepository:
    """Implementa UserRepository sobre PostgreSQL (o SQLite en pruebas)."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def get_by_phone(self, phone: PhoneNumber) -> User | None:
        return self._one(users.c.phone == phone.value)

    def get_by_id(self, user_id: str) -> User | None:
        return self._one(users.c.id == user_id)

    def get_by_email(self, email: EmailAddress) -> User | None:
        return self._one(users.c.email == email.value)

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
                    email=user.email.value if user.email else None,
                    verified_at=user.verified_at,
                )
            )
            if redeemed_code is None:
                return  # primera cuenta del equipo: no usa código de invitación
            session.execute(
                update(invitation_codes)
                .where(invitation_codes.c.code == redeemed_code.code)
                .values(used_by=redeemed_code.used_by, used_at=redeemed_code.used_at)
            )

    def mark_verified(self, user_id: str, at: datetime) -> None:
        with self._sessions() as session, session.begin():
            session.execute(update(users).where(users.c.id == user_id).values(verified_at=at))

    def record_login(self, user_id: str, at: datetime) -> None:
        with self._sessions() as session, session.begin():
            session.execute(update(users).where(users.c.id == user_id).values(last_login_at=at))

    def delete(self, user_id: str) -> None:
        # Todo o nada: la cuenta, su código pendiente y su código de invitación (queda libre)
        with self._sessions() as session, session.begin():
            session.execute(
                update(invitation_codes)
                .where(invitation_codes.c.used_by == user_id)
                .values(used_by=None, used_at=None)
            )
            session.execute(
                delete(verification_codes).where(verification_codes.c.user_id == user_id)
            )
            session.execute(delete(users).where(users.c.id == user_id))

    def count_admins(self) -> int:
        query = select(func.count()).where(users.c.role == Role.ADMIN.value)
        with self._sessions() as session:
            return int(session.execute(query).scalar_one())

    def participants(self) -> list[Participant]:
        query = (
            select(users, invitation_codes.c.code)
            .outerjoin(invitation_codes, invitation_codes.c.used_by == users.c.id)
            .order_by(users.c.created_at.desc())
        )
        with self._sessions() as session:
            rows = session.execute(query).all()
        return [
            Participant(
                user_id=row.id,
                phone=row.phone,
                role=Role(row.role),
                registered_at=row.created_at,
                invitation_code=row.code,
                last_login_at=row.last_login_at,
                email=row.email,
                verified=row.verified_at is not None,
            )
            for row in rows
        ]

    def _one(self, condition) -> User | None:  # type: ignore[no-untyped-def]
        with self._sessions() as session:
            row = session.execute(select(users).where(condition)).first()
        return _to_user(row) if row else None


def _to_user(row: Row) -> User:  # type: ignore[type-arg]
    return User(
        id=row.id,
        phone=PhoneNumber(row.phone),
        password_hash=row.password_hash,
        consent=Consent(row.consent_version, row.consent_accepted_at),
        created_at=row.created_at,
        role=Role(row.role),
        email=EmailAddress(row.email) if row.email else None,
        verified_at=row.verified_at,
    )


class SqlAlchemyVerificationRepository:
    """Implementa VerificationRepository: un código pendiente por cuenta."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def save(self, verification: Verification) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                delete(verification_codes).where(
                    verification_codes.c.user_id == verification.user_id
                )
            )
            session.execute(
                insert(verification_codes).values(
                    user_id=verification.user_id,
                    code=verification.code,
                    # En UTC: SQLite no guarda la zona horaria y se lee como UTC
                    created_at=verification.created_at.astimezone(UTC),
                    expires_at=verification.expires_at.astimezone(UTC),
                    attempts=verification.attempts,
                    delivered_by=verification.delivered_by,
                )
            )

    def get(self, user_id: str) -> Verification | None:
        query = select(verification_codes).where(verification_codes.c.user_id == user_id)
        with self._sessions() as session:
            row = session.execute(query).first()
        return _to_verification(row) if row else None

    def delete(self, user_id: str) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                delete(verification_codes).where(verification_codes.c.user_id == user_id)
            )

    def pending(self) -> dict[str, Verification]:
        with self._sessions() as session:
            rows = session.execute(select(verification_codes)).all()
        return {row.user_id: _to_verification(row) for row in rows}


def _to_verification(row: Row) -> Verification:  # type: ignore[type-arg]
    return Verification(
        user_id=row.user_id,
        code=row.code,
        created_at=_aware(row.created_at),
        expires_at=_aware(row.expires_at),
        attempts=row.attempts,
        delivered_by=row.delivered_by,
    )


def _aware(moment: datetime) -> datetime:
    # SQLite no guarda la zona horaria: se vuelve a poner UTC al leer
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


class SqlAlchemyInvitationCodeRepository:
    """Implementa InvitationCodeRepository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def get(self, code: str) -> InvitationCode | None:
        with self._sessions() as session:
            row = session.execute(
                select(invitation_codes).where(invitation_codes.c.code == code)
            ).first()
        return _to_code(row) if row else None

    def summary(self) -> CodeSummary:
        with self._sessions() as session:
            total, used = session.execute(
                select(func.count(), func.count(invitation_codes.c.used_by))
            ).one()
        return CodeSummary(total=int(total), used=int(used))

    def all(self) -> list[InvitationCode]:
        query = select(invitation_codes).order_by(
            invitation_codes.c.used_at.is_not(None),
            invitation_codes.c.used_at.desc(),
            invitation_codes.c.code,
        )
        with self._sessions() as session:
            rows = session.execute(query).all()
        return [_to_code(row) for row in rows]

    def add_many(self, codes: list[str], role: Role = Role.FARMER) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                insert(invitation_codes), [{"code": c, "role": role.value} for c in codes]
            )

    def delete(self, code: str) -> None:
        with self._sessions() as session, session.begin():
            session.execute(delete(invitation_codes).where(invitation_codes.c.code == code))


def _to_code(row: Row) -> InvitationCode:  # type: ignore[type-arg]
    return InvitationCode(row.code, row.used_by, row.used_at, Role(row.role))
