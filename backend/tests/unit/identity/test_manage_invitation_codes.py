"""El equipo genera los códigos del GE desde la app (Render no tiene terminal)."""

from itertools import cycle

import pytest

from identity.application.manage_invitation_codes import (
    InvalidCodeCountError,
    ManageInvitationCodes,
)
from identity.domain.invitation_code import CODE_ALPHABET, InvitationCode
from tests.fakes import InMemoryInvitationCodeRepository


def sequential_choice() -> object:
    """Elige los caracteres en orden: genera códigos predecibles para la prueba."""
    letters = cycle(CODE_ALPHABET)
    return lambda _alphabet: next(letters)


def test_generates_the_requested_number_of_new_codes() -> None:
    repository = InMemoryInvitationCodeRepository(InvitationCode("DEMO-0001"))
    manage = ManageInvitationCodes(repository, sequential_choice())  # type: ignore[arg-type]

    created = manage.generate(3)

    assert len(created) == 3
    assert len(set(created)) == 3
    assert all(code.startswith("JAEN-") and len(code) == 11 for code in created)
    assert {c.code for c in manage.list()} == {"DEMO-0001", *created}


def test_never_repeats_an_existing_code() -> None:
    first = "JAEN-" + CODE_ALPHABET[:6]
    repository = InMemoryInvitationCodeRepository(InvitationCode(first))
    manage = ManageInvitationCodes(repository, sequential_choice())  # type: ignore[arg-type]

    created = manage.generate(1)

    assert created != [first]


@pytest.mark.parametrize("count", [0, 51])
def test_rejects_invalid_amounts(count: int) -> None:
    manage = ManageInvitationCodes(InMemoryInvitationCodeRepository(), sequential_choice())  # type: ignore[arg-type]

    with pytest.raises(InvalidCodeCountError):
        manage.generate(count)


def test_lists_free_codes_first() -> None:
    repository = InMemoryInvitationCodeRepository(
        InvitationCode("DEMO-0001", used_by="u1"), InvitationCode("DEMO-0002")
    )
    manage = ManageInvitationCodes(repository, sequential_choice())  # type: ignore[arg-type]

    assert [c.code for c in manage.list()] == ["DEMO-0002", "DEMO-0001"]
