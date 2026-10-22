"""PA-02-1 y PA-02-2 (HU02): consenso entre varias webs del mismo precio."""

from datetime import datetime
from decimal import Decimal

import pytest

from market.domain.consensus import Consensus
from market.domain.errors import NoQuotationError, SourcesDisagreeError
from tests.fakes import LIMA, live

AT = datetime(2026, 11, 4, 9, 30, tzinfo=LIMA)


def test_publishes_median_when_three_sources_agree() -> None:
    result = Consensus().consolidate(
        [live("300.10", AT, "Yahoo"), live("300.20", AT, "Stooq"), live("300.15", AT, "Barchart")]
    )

    assert result.quote.cents_per_pound == Decimal("300.15")
    assert result.quote.sources == ("Yahoo", "Stooq", "Barchart")
    assert result.discarded == ()


def test_discards_source_far_from_the_median() -> None:
    result = Consensus().consolidate(
        [live("300", AT, "Yahoo"), live("300", AT, "Stooq"), live("310", AT, "Rara")]
    )

    assert result.quote.cents_per_pound == Decimal("300")
    assert result.discarded == ("Rara",)


def test_uses_most_recent_time_among_agreeing_sources() -> None:
    later = AT.replace(minute=31)

    result = Consensus().consolidate([live("300", AT, "Yahoo"), live("300.5", later, "Stooq")])

    assert result.quote.quoted_at == later


def test_two_sources_that_disagree_publish_nothing() -> None:
    with pytest.raises(SourcesDisagreeError):
        Consensus().consolidate([live("300", AT, "Yahoo"), live("320", AT, "Stooq")])


def test_without_sources_fails_clearly() -> None:
    with pytest.raises(NoQuotationError):
        Consensus().consolidate([])
