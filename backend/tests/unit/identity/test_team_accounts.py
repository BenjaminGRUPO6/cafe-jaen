"""El equipo crea cuentas de administrador directamente y cada cuenta ve su perfil."""

import pytest

from identity.application.create_team_account import CreateTeamAccount, TeamAccountCommand
from identity.application.get_profile import GetProfile
from identity.domain.errors import (
    InvalidNameError,
    InvalidPhoneError,
    PhoneAlreadyRegisteredError,
    WeakPasswordError,
)
from identity.domain.user import Role
from tests.fakes import FakePasswordHasher, FixedClock, InMemoryUserRepository


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


def create(users: InMemoryUserRepository, **overrides: str) -> object:
    data = {"name": "  Jhon   Chávez ", "phone": "955000111", "password": "equipo2026!"}
    data.update(overrides)
    return CreateTeamAccount(users, FakePasswordHasher(), FixedClock()).execute(
        TeamAccountCommand(**data)
    )


def test_creates_an_active_team_account_with_its_name(users: InMemoryUserRepository) -> None:
    account = create(users)

    profile = GetProfile(users).execute(account.id)  # type: ignore[attr-defined]
    assert profile.role is Role.ADMIN and profile.is_verified
    assert profile.display_name == "Jhon Chávez"


def test_without_name_the_profile_shows_the_phone(users: InMemoryUserRepository) -> None:
    account = create(users, name="")

    assert GetProfile(users).execute(account.id).display_name == "955000111"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"password": "corta"}, WeakPasswordError),
        ({"phone": "12345"}, InvalidPhoneError),
        ({"name": "x" * 81}, InvalidNameError),
    ],
)
def test_validates_the_data(
    users: InMemoryUserRepository, overrides: dict[str, str], error: type[Exception]
) -> None:
    with pytest.raises(error):
        create(users, **overrides)


def test_the_phone_cannot_repeat(users: InMemoryUserRepository) -> None:
    create(users)
    with pytest.raises(PhoneAlreadyRegisteredError):
        create(users, name="Otro")
