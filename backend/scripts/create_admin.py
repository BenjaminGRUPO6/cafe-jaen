"""Crea una cuenta de administrador del equipo (HU12: anotar precios de cooperativas).

Uso:  python scripts/create_admin.py --phone 987654321
La contraseña se pide por teclado (no queda en el historial de la terminal).
"""

import argparse
import getpass

from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User
from identity.infrastructure.persistence.sqlalchemy_repositories import SqlAlchemyUserRepository
from identity.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock

MIN_PASSWORD_LENGTH = 8


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phone", required=True)
    phone = PhoneNumber(parser.parse_args().phone)
    password = getpass.getpass("Contraseña del administrador: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres")

    users = SqlAlchemyUserRepository(
        create_session_factory(create_db_engine(get_settings().database_url))
    )
    if users.get_by_phone(phone):
        raise SystemExit("Ese celular ya está registrado")
    users.add(
        User.create_admin(phone, BcryptPasswordHasher().hash(password), SystemClock().now()), None
    )
    print(f"Administrador creado: {phone.value}")


if __name__ == "__main__":
    main()
