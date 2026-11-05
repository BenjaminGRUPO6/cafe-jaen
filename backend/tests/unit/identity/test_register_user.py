"""Pruebas de aceptación PA-01-1 a PA-01-4 (HU01) a nivel de caso de uso."""

import pytest

from identity.application.authenticate_user import AuthenticateUser
from identity.application.list_participants import ListParticipants
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.domain.errors import (
    AccountNotVerifiedError,
    ConsentNotAcceptedError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidInvitationCodeError,
    InvalidPhoneError,
    PhoneAlreadyRegisteredError,
    WeakPasswordError,
)
from identity.domain.invitation_code import InvitationCode
from identity.domain.user import Role
from tests.fakes import (
    FakePasswordHasher,
    FakeTokenIssuer,
    FixedClock,
    InMemoryInvitationCodeRepository,
    InMemoryUserRepository,
    InMemoryVerificationRepository,
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
        "email": "Caficultor@Gmail.com ",
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
        second.execute(command(invitation_code="JAEN-XYZ789", email="otro@gmail.com"))


def test_rejects_duplicated_email(register: RegisterUser, users: InMemoryUserRepository) -> None:
    register.execute(command())
    codes = InMemoryInvitationCodeRepository(InvitationCode("JAEN-XYZ789"))
    second = RegisterUser(users, codes, FakePasswordHasher(), FixedClock(), "2026-10")

    with pytest.raises(EmailAlreadyRegisteredError):
        second.execute(command(invitation_code="JAEN-XYZ789", phone="911111111"))


@pytest.mark.parametrize("email", ["", "sin-arroba", "a@b", "con espacio@gmail.com"])
def test_rejects_invalid_emails(register: RegisterUser, email: str) -> None:
    with pytest.raises(InvalidEmailError):
        register.execute(command(email=email))


def test_new_accounts_start_unverified_with_the_email_normalized(register: RegisterUser) -> None:
    user = register.execute(command())

    assert not user.is_verified
    assert user.email is not None and user.email.value == "caficultor@gmail.com"
    assert user.email.masked() == "ca***@gmail.com"


def test_a_team_code_creates_a_team_account(users: InMemoryUserRepository) -> None:
    codes = InMemoryInvitationCodeRepository(InvitationCode("EQUIPO-ABC234", role=Role.ADMIN))
    register = RegisterUser(users, codes, FakePasswordHasher(), FixedClock(), "2026-10")

    user = register.execute(command(invitation_code="equipo-abc234"))

    assert user.role is Role.ADMIN


def test_login_asks_for_the_code_until_the_account_is_verified(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    user = register.execute(command())
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer(), FixedClock())

    with pytest.raises(AccountNotVerifiedError):
        authenticate.execute("987654321", "cafe2026!")
    with pytest.raises(InvalidCredentialsError):  # con otra contraseña no revela nada
        authenticate.execute("987654321", "incorrecta")
    users.mark_verified(user.id, FixedClock().now())
    assert authenticate.execute("987654321", "cafe2026!").startswith("token-")


def test_login_returns_token_for_valid_credentials(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    user = register.execute(command())
    users.mark_verified(user.id, FixedClock().now())
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer(), FixedClock())

    assert authenticate.execute("987654321", "cafe2026!") == f"token-{user.id}-farmer"


@pytest.mark.parametrize(
    ("phone", "password"), [("987654321", "incorrecta"), ("911111111", "cafe2026!"), ("abc", "x")]
)
def test_login_rejects_invalid_credentials(
    register: RegisterUser, users: InMemoryUserRepository, phone: str, password: str
) -> None:
    register.execute(command())
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer(), FixedClock())

    with pytest.raises(InvalidCredentialsError):
        authenticate.execute(phone, password)


def test_login_records_the_last_login(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    user = register.execute(command())
    users.mark_verified(user.id, FixedClock().now())
    clock = FixedClock()
    authenticate = AuthenticateUser(users, FakePasswordHasher(), FakeTokenIssuer(), clock)

    authenticate.execute("987654321", "cafe2026!")

    assert users.logins[user.id] == clock.now()


def test_participants_report_lists_users_and_codes(
    register: RegisterUser, users: InMemoryUserRepository
) -> None:
    register.execute(command())
    codes = InMemoryInvitationCodeRepository(
        InvitationCode("JAEN-ABC234", used_by="x"), InvitationCode("JAEN-XYZ789")
    )

    report = ListParticipants(users, codes, InMemoryVerificationRepository()).execute()

    assert [p.phone for p in report.participants] == ["987654321"]
    assert report.participants[0].invitation_code == "JAEN-ABC234"
    assert report.participants[0].last_login_at is None
    assert (report.codes.total, report.codes.used) == (2, 1)
