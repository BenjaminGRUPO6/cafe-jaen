from sqlalchemy import Row, delete, exists, func, insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from market.domain.cooperative import Cooperative
from market.infrastructure.persistence.tables import cooperatives, local_price_observations


class SqlAlchemyCooperativeRepository:
    """Implementa CooperativeRepository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def all(self) -> list[Cooperative]:
        query = select(cooperatives).order_by(cooperatives.c.active.desc(), cooperatives.c.name)
        with self._sessions() as session:
            return [_cooperative(row) for row in session.execute(query)]

    def get(self, cooperative_id: int) -> Cooperative | None:
        query = select(cooperatives).where(cooperatives.c.id == cooperative_id)
        with self._sessions() as session:
            row = session.execute(query).first()
        return _cooperative(row) if row else None

    def get_by_name(self, name: str) -> Cooperative | None:
        query = select(cooperatives).where(func.lower(cooperatives.c.name) == name.strip().lower())
        with self._sessions() as session:
            row = session.execute(query).first()
        return _cooperative(row) if row else None

    def add(self, cooperative: Cooperative) -> Cooperative:
        with self._sessions() as session, session.begin():
            new_id = session.execute(
                insert(cooperatives)
                .values(
                    name=cooperative.name,
                    location=cooperative.location,
                    website=cooperative.website,
                    active=cooperative.active,
                )
                .returning(cooperatives.c.id)
            ).scalar_one()
        return Cooperative(
            new_id, cooperative.name, cooperative.location, cooperative.website, cooperative.active
        )

    def update(self, cooperative: Cooperative, previous_name: str) -> None:
        # En una sola transacción: el catálogo y los precios anotados quedan con el mismo nombre
        with self._sessions() as session, session.begin():
            session.execute(
                update(cooperatives)
                .where(cooperatives.c.id == cooperative.id)
                .values(
                    name=cooperative.name,
                    location=cooperative.location,
                    website=cooperative.website,
                    active=cooperative.active,
                )
            )
            if cooperative.name != previous_name:
                session.execute(
                    update(local_price_observations)
                    .where(local_price_observations.c.cooperative == previous_name)
                    .values(cooperative=cooperative.name)
                )

    def delete(self, cooperative_id: int) -> None:
        with self._sessions() as session, session.begin():
            session.execute(delete(cooperatives).where(cooperatives.c.id == cooperative_id))

    def has_prices(self, name: str) -> bool:
        query = select(exists().where(local_price_observations.c.cooperative == name))
        with self._sessions() as session:
            return bool(session.execute(query).scalar())


def _cooperative(row: Row) -> Cooperative:  # type: ignore[type-arg]
    return Cooperative(row.id, row.name, row.location, row.website, bool(row.active))
