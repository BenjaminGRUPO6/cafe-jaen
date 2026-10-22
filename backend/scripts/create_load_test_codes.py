"""Crea los códigos LOAD-001 … LOAD-030 para la prueba de carga (solo en entornos de prueba)."""

from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
)
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings

USERS = 30


def main() -> None:
    sessions = create_session_factory(create_db_engine(get_settings().database_url))
    SqlAlchemyInvitationCodeRepository(sessions).add_many(
        [f"LOAD-{n:03d}" for n in range(1, USERS + 1)]
    )
    print(f"{USERS} códigos de prueba de carga creados")


if __name__ == "__main__":
    main()
