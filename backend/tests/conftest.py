"""Fixtures compartidas: aplicación completa sobre SQLite con fuentes externas simuladas."""

import math
from collections.abc import Iterator
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

# Importar las tablas las registra en el metadata compartido
import forecasting.infrastructure.persistence.tables  # noqa: F401
import identity.infrastructure.persistence.tables  # noqa: F401
import market.infrastructure.persistence.tables  # noqa: F401
import orchestration.infrastructure.persistence.tables  # noqa: F401
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User
from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
    SqlAlchemyUserRepository,
)
from identity.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from main import Overrides, create_app
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory, metadata
from shared.infrastructure.settings import Settings
from tests.fakes import LIMA, FakeProvider, FixedClock, business_days, live, quotation, rate, source

INVITATION_CODE = "JAEN-TEST01"


@pytest.fixture
def clock() -> FixedClock:
    # Hora real (un minuto atrás): los tokens JWT se validan contra el reloj del sistema
    return FixedClock(datetime.now(LIMA) - timedelta(minutes=1))


@pytest.fixture
def sessions(tmp_path) -> Iterator[sessionmaker[Session]]:  # type: ignore[no-untyped-def]
    engine = create_db_engine(f"sqlite:///{tmp_path / 'test.db'}")
    metadata.create_all(engine)
    yield create_session_factory(engine)
    engine.dispose()


@pytest.fixture
def seeded_sessions(sessions: sessionmaker[Session], clock: FixedClock) -> sessionmaker[Session]:
    """150 días hábiles de cierres hasta ayer y un código de invitación."""
    prices = SqlAlchemyPriceRepository(sessions)
    days = business_days(clock.today() - timedelta(days=1), 150)
    prices.add_exchange_rate(rate("3.75", days[0]))
    for index, day in enumerate(days):
        cents = Decimal(f"{290 + 10 * math.sin(index / 8):.2f}")
        prices.save_daily_close(quotation(str(cents), day))
    SqlAlchemyInvitationCodeRepository(sessions).add_many([INVITATION_CODE])
    return sessions


@pytest.fixture
def client(
    seeded_sessions: sessionmaker[Session], clock: FixedClock, tmp_path
) -> Iterator[TestClient]:  # type: ignore[no-untyped-def]
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        jwt_secret="test-secret-with-at-least-32-bytes!!",
        scheduler_enabled=False,
        forecast_history_days=400,
        llm_provider="keyword",
        stream_poll_seconds=0.01,
        stream_max_events=1,
    )
    overrides = Overrides(
        # Dos webs que coinciden: 300 ¢/lb hace 2 minutos
        quotation_sources=[
            source("Yahoo Finance", live("300", clock.now() - timedelta(minutes=2))),
            source("Stooq", live("300", clock.now() - timedelta(minutes=2))),
        ],
        exchange_rate_provider=FakeProvider(rate("3.75", clock.today())),
        clock=clock,
    )
    with TestClient(create_app(settings, overrides)) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/register",
        json={
            "invitation_code": INVITATION_CODE,
            "phone": "987654321",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client: TestClient, seeded_sessions: sessionmaker[Session]) -> dict[str, str]:
    """Administrador del equipo creado como lo hace scripts/create_admin.py."""
    users = SqlAlchemyUserRepository(seeded_sessions)
    admin = User.create_admin(
        PhoneNumber("911111111"), BcryptPasswordHasher().hash("equipo2026!"), datetime.now(LIMA)
    )
    users.add(admin, None)
    response = client.post(
        "/api/auth/login", json={"phone": "911111111", "password": "equipo2026!"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
