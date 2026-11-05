"""Webs reales de la bolsa que puede consultar el Recolector (`QUOTATION_SOURCES`)."""

import logging
from collections.abc import Callable, Sequence

from market.domain.ports.sources import QuotationSource
from market.infrastructure.sources.cnbc_quotation_source import CnbcQuotationSource
from market.infrastructure.sources.stooq_quotation_source import StooqQuotationSource
from market.infrastructure.sources.tradingview_quotation_source import TradingViewQuotationSource
from market.infrastructure.sources.yahoo_quotation_source import YahooQuotationSource

logger = logging.getLogger(__name__)

DEFAULT_SOURCES = ("yahoo", "stooq", "cnbc", "tradingview")


def build_sources(names: Sequence[str], stooq_timezone: str) -> list[QuotationSource]:
    """Un adaptador por cada web configurada (agregar una web = agregar un adaptador).

    Un nombre desconocido (por ejemplo, el antiguo «demo») se ignora con un aviso en vez de
    impedir que la app arranque; si no queda ninguna web válida, se usan las cuatro webs reales.
    """
    available: dict[str, Callable[[], QuotationSource]] = {
        "yahoo": YahooQuotationSource,
        "stooq": lambda: StooqQuotationSource(timezone=stooq_timezone),
        "cnbc": CnbcQuotationSource,
        "tradingview": TradingViewQuotationSource,
    }
    unknown = [name for name in names if name not in available]
    if unknown:
        logger.warning(
            "QUOTATION_SOURCES tiene webs desconocidas %s: se ignoran (válidas: %s)",
            unknown,
            ", ".join(available),
        )
    valid = [name for name in dict.fromkeys(names) if name in available] or list(DEFAULT_SOURCES)
    return [available[name]() for name in valid]
