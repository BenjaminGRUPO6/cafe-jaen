"""Genera los códigos de invitación para el grupo experimental (HU01).

Uso:  python scripts/create_invitation_codes.py --count 30
Los códigos se imprimen para entregarlos en sobre cerrado a cada participante del GE.
"""

import argparse
import secrets

from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
)
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings

# Sin letras ni números que se confunden al leerlos (0/O, 1/I/L)
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def new_code() -> str:
    return "JAEN-" + "".join(secrets.choice(ALPHABET) for _ in range(6))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=30)
    count = parser.parse_args().count

    codes = sorted({new_code() for _ in range(count * 2)})[:count]
    sessions = create_session_factory(create_db_engine(get_settings().database_url))
    SqlAlchemyInvitationCodeRepository(sessions).add_many(codes)
    print("\n".join(codes))


if __name__ == "__main__":
    main()
