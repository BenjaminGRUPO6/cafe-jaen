"""PA-03-1 (HU03): conversión de ¢USD/lb a soles por quintal."""

from decimal import Decimal

import pytest

from market.domain.quintal_price import PriceConverter, QuintalPrice


def test_converts_ice_quote_to_soles_per_quintal() -> None:
    # 300 ¢/lb con tipo de cambio 3,75 debe dar S/ 1140,89 por quintal
    converter = PriceConverter()

    result = converter.to_quintal(Decimal("300"), Decimal("3.75"))

    assert result.soles == Decimal("1140.89")


@pytest.mark.parametrize(
    ("cents", "rate", "factor", "expected"),
    [
        ("250", "3.70", "1", "938.07"),
        ("400", "3.80", "1", "1541.47"),
        ("300", "3.75", "0.90", "1026.80"),
        ("100", "3.50", "1", "354.94"),
    ],
)
def test_conversion_matches_manual_calculation(
    cents: str, rate: str, factor: str, expected: str
) -> None:
    # Los valores esperados se calcularon a mano: ¢/100 × 101,4126 lb × TC × factor
    converter = PriceConverter(Decimal(factor))

    assert converter.to_quintal(Decimal(cents), Decimal(rate)).soles == Decimal(expected)


def test_price_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="negativo"):
        QuintalPrice(Decimal("-1"))
