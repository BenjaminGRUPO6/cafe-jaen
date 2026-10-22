"""Pruebas de aceptación PA-01-1 a PA-01-4 (HU01) a nivel de caso de uso."""

import pytest

from identity.application.authenticate_user import AuthenticateUser
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.domain.errors import (
    ConsentNotAcceptedError,
    InvalidCredentialsError,
    InvalidInvitationCodeError,
    InvalidPhoneError,
    PhoneAlreadyRegisteredError,
    WeakPasswordError,
)
from identity.domain.invitation_code import InvitationCode
from tests.fakes import (
    FakePasswordHasher,
    FakeTokenIssuer,
    FixedClock,
    InMemoryInvitationCodeRepository,
    InMemoryUserRepository,
)


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def register(users: InMemoryUserRepository) -> RegisterUser:
    codes = InMemoryInvitationCodeRepository(InvitationCode("JAEN-ABC234"))
    return RegisterUser(users, codes, FakePasswordHasher(), FixedClock(), consent_version="2026-10")


def command(**overrides: object) -> RegisterUserCommand:
    data = {
        "invitation_code": "jaen-abc234",
        "phone": "987654321",
        "password": "cafe2026!",
        "consent_accepted": True,
    }
    data.update(overrides)
    return RegisterUserCommand(**data)  # type: ignore[arg-type]


def test_registers_user_and_redeems_code(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    # PA-01-1
    user = register.execute(command())

    assert user.phone.value == "987654321"
    assert users.redeemed[0].used_by == user.id


def test_rejects_unknown_code(register: RegisterUser) -> None:
    # PA-01-2: un participante del GC no tiene código válido
    with pytest.raises(InvalidInvitationCodeError):
        register.execute(command(invitation_code="NO-EXISTE"))


def test_rejects_used_code(users: InMemoryUserRepository) -> None:
    used = InvitationCode("JAEN-ABC234", used_by="otro-usuario")
    register = RegisterUser(
        users, InMemoryInvitationCodeRepository(used), FakePasswordHasher(), FixedClock(), "2026-10"
    )

    with pytest.raises(InvalidInvitationCodeError):
        register.execute(command())


def test_requires_consent(register: RegisterUser) -> None:
    # PA-01-3
    with pytest.raises(ConsentNotAcceptedError):
        register.execute(command(consent_accepted=False))


def test_stores_consent_version_and_date(register: RegisterUser) -> None:
    user = register.execute(command())

    assert user.consent.version == "2026-10"
    assert user.consent.accepted_at == FixedClock().now()


def test_password_is_never_stored_in_plain_text(register: RegisterUser) -> None:
    # PA-01-4
    user = register.execute(command())

    assert user.password_hash != "cafe2026!"


@pytest.mark.parametrize("password", ["", "corta", "1234567"])
def test_rejects_short_passwords(register: RegisterUser, password: str) -> None:
    with pytest.raises(WeakPasswordError):
        register.execute(command(password=password))


@pytest.mark.parametrize("phone", ["12345678", "887654321", "98765432a"])
def test_rejects_invalid_phones(register: RegisterUser, phone: str) -> None:
    with pytest.raises(InvalidPhoneError):
        register.execute(command(phone=phone))


def test_rejects_duplicated_phone(register: RegisterUser, users: InMemoryUserRepository) -> None:
    register.execute(command())
    codes = InMemoryInvitationCodeRepository(InvitationCode("JAEN-XYZ789"))
    second = RegisterUser(users, codes, FakePasswordHasher(), FixedClock(), "2026-10")

    with pytest.raises(PhoneAlreadyRegisteredError):
        second.execute(command(invitation_code="JAEN-XYZ789"))


def test_login_returns_token_for_valid_credentials(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    user = register.execute(command())
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer())

    assert authenticate.execute("987654321", "cafe2026!") == f"token-{user.id}-farmer"


@pytest.mark.parametrize(
    ("phone", "password"), [("987654321", "incorrecta"), ("911111111", "cafe2026!"), ("abc", "x")]
)
def test_login_rejects_invalid_credentials(
    register: RegisterUser, users: InMemoryUserRepository, phone: str, password: str
) -> None:
    register.execute(command())
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer())

    with pytest.raises(InvalidCredentialsError):
        authenticate.execute(phone, password)
