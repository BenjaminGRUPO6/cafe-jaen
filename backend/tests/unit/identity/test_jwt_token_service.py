"""PA-01-4 (HU01): la sesión dura 30 días y un token alterado no es válido."""

from datetime import datetime, timedelta

import jwt

from identity.infrastructure.security.jwt_token_service import JwtTokenService
from tests.fakes import LIMA, FixedClock

SECRET = "secreto-de-pruebas-con-al-menos-32-bytes"


def test_token_identifies_the_user_and_lasts_thirty_days() -> None:
    clock = FixedClock(datetime.now(LIMA) - timedelta(minutes=1))
    service = JwtTokenService(SECRET, session_days=30, clock=clock)

    token = service.issue("user-1")
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])

    assert service.verify(token) == "user-1"
    assert payload["exp"] - payload["iat"] == int(timedelta(days=30).total_seconds())


def test_tampered_or_expired_tokens_are_rejected() -> None:
    expired = JwtTokenService(SECRET, 30, FixedClock(datetime.now(LIMA) - timedelta(days=31)))
    valid = JwtTokenService(SECRET, 30, FixedClock(datetime.now(LIMA) - timedelta(minutes=1)))

    assert valid.verify(expired.issue("user-1")) is None
    assert valid.verify(valid.issue("user-1") + "x") is None


def test_token_carries_the_role_for_team_routes() -> None:
    # HU12: solo el equipo (rol admin) puede anotar precios de cooperativas
    service = JwtTokenService(SECRET, 30, FixedClock(datetime.now(LIMA) - timedelta(minutes=1)))

    assert service.role(service.issue("user-1")) == "farmer"
    assert service.role(service.issue("admin-1", "admin")) == "admin"
    assert service.role("no-es-un-token") is None
