"""Verificación del correo al registrarse y eliminación de cuentas por el equipo."""

from datetime import timedelta
from itertools import cycle

import pytest

from identity.application.delete_participant import DeleteParticipant
from identity.application.email_verification import SendVerificationCode, VerifyAccount
from identity.application.list_participants import ListParticipants
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.domain.errors import (
    AlreadyVerifiedError,
    CannotDeleteSelfError,
    InvalidVerificationCodeError,
    LastAdminError,
    ResendTooSoonError,
    TooManyAttemptsError,
    VerificationExpiredError,
)
from identity.domain.invitation_code import InvitationCode
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User
from tests.fakes import (
    FakeEmailSender,
    FakePasswordHasher,
    FakeTokenIssuer,
    FixedClock,
    InMemoryInvitationCodeRepository,
    InMemoryUserRepository,
    InMemoryVerificationRepository,
)


class World:
    def __init__(self, sender: FakeEmailSender | None = None) -> None:
        self.clock = FixedClock()
        self.users = InMemoryUserRepository()
        self.codes = InMemoryInvitationCodeRepository(InvitationCode("JAEN-ABC234"))
        self.verifications = InMemoryVerificationRepository()
        self.sender = sender or FakeEmailSender()
        digits = cycle("123456")
        self.send = SendVerificationCode(
            self.users, self.verifications, self.sender, self.clock, lambda _: next(digits)
        )
        self.verify = VerifyAccount(self.users, self.verifications, FakeTokenIssuer(), self.clock)

    def register(self) -> User:
        user = RegisterUser(
            self.users, self.codes, FakePasswordHasher(), self.clock, "2026-10"
        ).execute(
            RegisterUserCommand("JAEN-ABC234", "987654321", "cafe2026!", True, "luis@gmail.com")
        )
        self.send.for_new_user(user)
        return user


def test_the_code_arrives_by_email_and_opens_the_session() -> None:
    world = World()
    user = world.register()

    assert world.sender.sent[0][0] == "luis@gmail.com"
    assert world.sender.last_code() == "123456"
    token = world.verify.execute("987654321", "123456")

    assert token == f"token-{user.id}-farmer"
    assert world.users.get_by_id(user.id).is_verified  # type: ignore[union-attr]
    assert world.verifications.get(user.id) is None


def test_if_the_email_fails_the_team_sees_the_code() -> None:
    world = World(FakeEmailSender(fail=True))
    user = world.register()

    report = ListParticipants(world.users, world.codes, world.verifications).execute()

    participant = report.participants[0]
    assert participant.user_id == user.id
    assert (participant.verified, participant.pending_code) == (False, "123456")
    assert participant.code_emailed is False


def test_wrong_codes_count_attempts_until_blocked() -> None:
    world = World()
    world.register()

    with pytest.raises(InvalidVerificationCodeError, match="4 intentos"):
        world.verify.execute("987654321", "000000")
    for _ in range(4):
        with pytest.raises(InvalidVerificationCodeError):
            world.verify.execute("987654321", "000000")
    with pytest.raises(TooManyAttemptsError):
        world.verify.execute("987654321", "123456")


def test_the_code_expires_after_15_minutes() -> None:
    world = World()
    world.register()
    world.clock.current += timedelta(minutes=16)

    with pytest.raises(VerificationExpiredError):
        world.verify.execute("987654321", "123456")


def test_a_new_code_can_be_requested_once_per_minute() -> None:
    world = World()
    world.register()

    with pytest.raises(ResendTooSoonError):
        world.send.resend("987654321")
    world.clock.current += timedelta(seconds=61)
    _, sent = world.send.resend("987654321")

    assert sent and len(world.sender.sent) == 2


def test_a_verified_account_does_not_ask_for_codes() -> None:
    world = World()
    world.register()
    world.verify.execute("987654321", "123456")

    with pytest.raises(AlreadyVerifiedError):
        world.send.resend("987654321")


def test_the_team_deletes_an_account_and_frees_its_code() -> None:
    world = World()
    user = world.register()
    admin = User.create_admin(PhoneNumber("900000001"), "x", world.clock.now())
    world.users.add(admin, None)

    DeleteParticipant(world.users).execute(user.id, requested_by=admin.id)

    assert world.users.get_by_id(user.id) is None
    assert world.users.redeemed == []


def test_nobody_deletes_themselves_or_the_last_team_account() -> None:
    world = World()
    farmer = world.register()
    admin = User.create_admin(PhoneNumber("900000001"), "x", world.clock.now())
    world.users.add(admin, None)

    with pytest.raises(CannotDeleteSelfError):
        DeleteParticipant(world.users).execute(admin.id, requested_by=admin.id)
    with pytest.raises(LastAdminError):
        DeleteParticipant(world.users).execute(admin.id, requested_by=farmer.id)
