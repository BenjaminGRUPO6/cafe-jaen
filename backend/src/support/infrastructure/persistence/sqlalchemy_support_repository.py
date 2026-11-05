from datetime import UTC, datetime

from sqlalchemy import Row, and_, func, insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from support.domain.support_message import Author, SupportMessage, ThreadSummary
from support.infrastructure.persistence.tables import support_messages as table


class SqlAlchemySupportRepository:
    """Implementa SupportRepository sobre PostgreSQL (o SQLite en pruebas)."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def add(self, message: SupportMessage) -> SupportMessage:
        with self._sessions() as session, session.begin():
            new_id = session.execute(
                insert(table)
                .values(
                    user_id=message.user_id,
                    author=message.author.value,
                    text=message.text,
                    created_at=message.created_at.astimezone(UTC),
                    read=message.read,
                )
                .returning(table.c.id)
            ).scalar_one()
        return SupportMessage(
            message.user_id, message.author, message.text, message.created_at, message.read, new_id
        )

    def thread(self, user_id: str) -> list[SupportMessage]:
        query = select(table).where(table.c.user_id == user_id).order_by(table.c.id)
        with self._sessions() as session:
            return [_to_message(row) for row in session.execute(query)]

    def threads(self) -> list[ThreadSummary]:
        last = (
            select(table.c.user_id, func.max(table.c.id).label("last_id"))
            .group_by(table.c.user_id)
            .subquery()
        )
        unread = (
            select(table.c.user_id, func.count().label("unread"))
            .where(and_(table.c.author == Author.FARMER.value, table.c.read.is_(False)))
            .group_by(table.c.user_id)
            .subquery()
        )
        query = (
            select(table, func.coalesce(unread.c.unread, 0).label("unread"))
            .join(last, table.c.id == last.c.last_id)
            .outerjoin(unread, unread.c.user_id == table.c.user_id)
        )
        with self._sessions() as session:
            rows = session.execute(query).all()
        summaries = [
            ThreadSummary(
                user_id=row.user_id,
                last_text=row.text,
                last_at=_utc(row.created_at),
                last_author=Author(row.author),
                unread=int(row.unread),
            )
            for row in rows
        ]
        # Primero las que esperan respuesta; dentro de cada grupo, la más reciente primero
        return sorted(summaries, key=lambda s: (s.unread == 0, -s.last_at.timestamp()))

    def mark_read(self, user_id: str, written_by: Author) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                update(table)
                .where(table.c.user_id == user_id, table.c.author == written_by.value)
                .values(read=True)
            )

    def unread(self, user_id: str, written_by: Author) -> int:
        query = select(func.count()).where(
            table.c.user_id == user_id,
            table.c.author == written_by.value,
            table.c.read.is_(False),
        )
        with self._sessions() as session:
            return int(session.execute(query).scalar_one())


def _to_message(row: Row) -> SupportMessage:  # type: ignore[type-arg]
    return SupportMessage(
        row.user_id, Author(row.author), row.text, _utc(row.created_at), row.read, row.id
    )


def _utc(moment: datetime) -> datetime:
    # SQLite no guarda la zona horaria: se vuelve a poner UTC al leer
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)
