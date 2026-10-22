from dataclasses import dataclass

from identity.domain.errors import (
    ConsentNotAcceptedError,
    InvalidInvitationCodeError,
    PhoneAlreadyRegisteredError,
    WeakPasswordError,
)
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.security import PasswordHasher
from identity.domain.ports.user_repository import InvitationCodeRepository, UserRepository
from identity.domain.user import Consent, User
from shared.domain.ports.clock import Clock

MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class RegisterUserCommand:
    invitation_code: str
    phone: str
    password: str
    consent_accepted: bool


class RegisterUser:
    """HU01: registra a un caficultor del GE con su código de invitación."""

    def __init__(
        self,
        users: UserRepository,
        codes: InvitationCodeRepository,
        hasher: PasswordHasher,
        clock: Clock,
        consent_version: str,
    ) -> None:
        self._users = users
        self._codes = codes
        self._hasher = hasher
        self._clock = clock
        self._consent_version = consent_version

    def execute(self, command: RegisterUserCommand) -> User:
        # El orden de las validaciones va de lo más barato a lo más costoso
        if not command.consent_accepted:
            raise ConsentNotAcceptedError()
        if len(command.password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(MIN_PASSWORD_LENGTH)
        phone = PhoneNumber(command.phone)

        code = self._codes.get(command.invitation_code.strip().upper())
        if code is None or code.is_used:
            raise InvalidInvitationCodeError()
        if self._users.get_by_phone(phone) is not None:
            raise PhoneAlreadyRegisteredError()

        now = self._clock.now()
        user = User.create(
            phone=phone,
            password_hash=self._hasher.hash(command.password),
            consent=Consent(self._consent_version, now),
            at=now,
        )
        self._users.add(user, code.redeem(user.id, now))
        return user
