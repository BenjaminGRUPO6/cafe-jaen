"""PA-02-2 (HU02): saltos atípicos y cotizaciones repetidas no se publican."""

from datetime import datetime

import pytest

from market.domain.errors import DuplicateQuotationError, OutlierQuotationError
from market.domain.price_validator import PriceValidator
from tests.fakes import LIMA, live

BEFORE = datetime(2026, 11, 4, 9, 0, tzinfo=LIMA)
NOW = datetime(2026, 11, 4, 9, 1, tzinfo=LIMA)


def test_accepts_first_quotation() -> None:
    PriceValidator().validate(live("300", NOW), last=None)


def test_accepts_normal_change() -> None:
    PriceValidator().validate(live("310", NOW), last=live("300", BEFORE))


def test_rejects_jump_bigger_than_ten_percent() -> None:
    with pytest.raises(OutlierQuotationError):
        PriceValidator().validate(live("340", NOW), last=live("300", BEFORE))


def test_rejects_quotation_that_is_not_newer() -> None:
    with pytest.raises(DuplicateQuotationError):
        PriceValidator().validate(live("301", BEFORE), last=live("300", BEFORE))
