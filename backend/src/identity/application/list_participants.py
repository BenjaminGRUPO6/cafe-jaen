from dataclasses import dataclass

from identity.domain.participant import CodeSummary, Participant
from identity.domain.ports.user_repository import InvitationCodeRepository, UserRepository


@dataclass(frozen=True)
class ParticipantsReport:
    participants: list[Participant]
    codes: CodeSummary


class ListParticipants:
    """Solo el equipo: quiénes del GE se registraron y cuándo entraron por última vez."""

    def __init__(self, users: UserRepository, codes: InvitationCodeRepository) -> None:
        self._users = users
        self._codes = codes

    def execute(self) -> ParticipantsReport:
        return ParticipantsReport(self._users.participants(), self._codes.summary())
