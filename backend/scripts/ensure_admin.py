"""Crea la cuenta del equipo a partir de ADMIN_PHONE y ADMIN_PASSWORD (si están definidas).

Lo ejecuta scripts/start_server.sh al arrancar en Render, donde el plan gratuito no tiene
terminal. En local se sigue usando `python dev.py admin 9XXXXXXXX`.
"""

from identity.application.ensure_admin import EnsureAdmin
from identity.domain.errors import IdentityError
from identity.infrastructure.persistence.sqlalchemy_repositories import SqlAlchemyUserRepository
from identity.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock


def main() -> None:
    settings = get_settings()
    if not settings.admin_phone:
        print("ADMIN_PHONE no está definido: no se crea cuenta del equipo.")
        return
    users = SqlAlchemyUserRepository(
        create_session_factory(create_db_engine(settings.database_url))
    )
    try:
        created = EnsureAdmin(users, BcryptPasswordHasher(), SystemClock()).execute(
            settings.admin_phone, settings.admin_password
        )
    except IdentityError as error:
        # Un dato mal escrito en Render no debe impedir que la app arranque
        print(f"No se creó la cuenta del equipo: {error}")
        return
    state = "creada" if created else "ya existe"
    print(f"Cuenta del equipo {settings.admin_phone}: {state}.")


if __name__ == "__main__":
    main()
