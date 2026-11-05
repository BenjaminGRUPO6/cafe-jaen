"""«Atención»: el caficultor pregunta, el equipo responde y cada uno ve lo que no leyó."""

import pytest

from support.application.support_inbox import FarmerSupport, TeamSupport
from support.domain.errors import EmptyMessageError, MessageTooLongError
from support.domain.support_message import Author, SupportMessage, ThreadSummary
from tests.fakes import FixedClock


class InMemorySupportRepository:
    def __init__(self) -> None:
        self.messages: list[SupportMessage] = []

    def add(self, message: SupportMessage) -> SupportMessage:
        saved = SupportMessage(
            message.user_id,
            message.author,
            message.text,
            message.created_at,
            message.read,
            len(self.messages) + 1,
        )
        self.messages.append(saved)
        return saved

    def thread(self, user_id: str) -> list[SupportMessage]:
        return [m for m in self.messages if m.user_id == user_id]

    def threads(self) -> list[ThreadSummary]:
        result = []
        for user_id in dict.fromkeys(m.user_id for m in self.messages):
            thread = self.thread(user_id)
            unread = sum(1 for m in thread if m.author is Author.FARMER and not m.read)
            last = thread[-1]
            result.append(ThreadSummary(user_id, last.text, last.created_at, last.author, unread))
        return sorted(result, key=lambda s: s.unread == 0)

    def mark_read(self, user_id: str, written_by: Author) -> None:
        self.messages = [
            SupportMessage(m.user_id, m.author, m.text, m.created_at, True, m.id)
            if m.user_id == user_id and m.author is written_by
            else m
            for m in self.messages
        ]

    def unread(self, user_id: str, written_by: Author) -> int:
        return sum(1 for m in self.thread(user_id) if m.author is written_by and not m.read)


@pytest.fixture
def repository() -> InMemorySupportRepository:
    return InMemorySupportRepository()


def test_the_team_sees_the_question_and_the_farmer_sees_the_reply(
    repository: InMemorySupportRepository,
) -> None:
    farmer, team = FarmerSupport(repository, FixedClock()), TeamSupport(repository, FixedClock())

    farmer.write("u1", "  ¿Por qué el precio en Jaén es menor que la bolsa?  ")
    assert team.inbox()[0].unread == 1
    team.conversation("u1")  # el equipo la abre: queda leída
    team.reply("u1", "Porque la cooperativa descuenta flete, secado y su margen.")

    assert team.inbox()[0].unread == 0
    assert farmer.unread_replies("u1") == 1
    messages = farmer.conversation("u1").messages
    assert [m.author for m in messages] == [Author.FARMER, Author.TEAM]
    assert messages[0].text.startswith("¿Por qué")  # sin espacios sobrantes
    assert farmer.unread_replies("u1") == 0


def test_each_farmer_only_sees_their_own_conversation(
    repository: InMemorySupportRepository,
) -> None:
    farmer = FarmerSupport(repository, FixedClock())
    farmer.write("u1", "Hola")
    farmer.write("u2", "Buenas")

    assert [m.text for m in farmer.conversation("u2").messages] == ["Buenas"]


@pytest.mark.parametrize(
    ("text", "error"), [("   ", EmptyMessageError), ("x" * 1001, MessageTooLongError)]
)
def test_rejects_empty_or_too_long_messages(
    repository: InMemorySupportRepository, text: str, error: type[Exception]
) -> None:
    with pytest.raises(error):
        FarmerSupport(repository, FixedClock()).write("u1", text)
