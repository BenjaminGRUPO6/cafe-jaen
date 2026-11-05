from dataclasses import dataclass, replace

from identity.domain.participant import CodeSummary, Participant
from identity.domain.ports.user_repository import (
    InvitationCodeRepository,
    UserRepository,
    VerificationRepository,
)


@dataclass(frozen=True)
class ParticipantsReport:
    participants: list[Participant]
    codes: CodeSummary


class ListParticipants:
    """Solo el equipo: quiénes del GE se registraron y cuándo entraron por última vez."""

    def __init__(
        self,
        users: UserRepository,
        codes: InvitationCodeRepository,
        verifications: VerificationRepository,
    ) -> None:
        self._users = users
        self._codes = codes
        self._verifications = verifications

    def execute(self) -> ParticipantsReport:
        # Las cuentas sin verificar llevan su código: el equipo puede enviarlo por WhatsApp
        pending = self._verifications.pending()
        participants = [
            replace(
                p,
                pending_code=pending[p.user_id].code,
                delivered_by=pending[p.user_id].delivered_by,
            )
            if p.user_id in pending and not p.verified
            else p
            for p in self._users.participants()
        ]
        return ParticipantsReport(participants, self._codes.summary())
