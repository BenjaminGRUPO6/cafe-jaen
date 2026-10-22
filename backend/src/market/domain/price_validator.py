from decimal import Decimal

from market.domain.errors import DuplicateQuotationError, OutlierQuotationError
from market.domain.quotation import LiveQuote


class PriceValidator:
    """Reglas para aceptar una cotización nueva (HU02)."""

    def __init__(self, max_change: Decimal = Decimal("0.10")) -> None:
        self._max_change = max_change

    def validate(self, new: LiveQuote, last: LiveQuote | None) -> None:
        """Lanza un error si la cotización no es más reciente que la última o es atípica."""
        if last is None:
            return  # la primera cotización no tiene contra qué compararse
        if new.quoted_at <= last.quoted_at:
            raise DuplicateQuotationError()
        change = abs(new.cents_per_pound - last.cents_per_pound) / last.cents_per_pound
        if change > self._max_change:
            raise OutlierQuotationError(float(change * 100))
