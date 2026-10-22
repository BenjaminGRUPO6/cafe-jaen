import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TypeVar

from market.domain.consensus import Consensus
from market.domain.errors import MarketError, SourceUnavailableError
from market.domain.market_hours import MarketHours
from market.domain.ports.price_repository import PriceRepository
from market.domain.ports.sources import ExchangeRateProvider, QuotationSource
from market.domain.price_validator import PriceValidator
from market.domain.quotation import LiveQuote, Quotation
from shared.domain.ports.clock import Clock

logger = logging.getLogger(__name__)
T = TypeVar("T")
MAX_ATTEMPTS = 3


@dataclass
class CollectionReport:
    """Resultado de una recolección: qué se guardó y qué incidentes hubo."""

    market_open: bool = False
    quotation_saved: bool = False
    exchange_rate_saved: bool = False
    sources_ok: list[str] = field(default_factory=list)
    sources_discarded: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


class CollectPrices:
    """HU02: consulta varias webs del precio de Nueva York, las consolida, valida y guarda."""

    def __init__(
        self,
        sources: Sequence[QuotationSource],
        exchange_rates: ExchangeRateProvider,
        repository: PriceRepository,
        consensus: Consensus,
        validator: PriceValidator,
        market_hours: MarketHours,
        clock: Clock,
    ) -> None:
        self._sources = sources
        self._exchange_rates = exchange_rates
        self._repository = repository
        self._consensus = consensus
        self._validator = validator
        self._market_hours = market_hours
        self._clock = clock

    def execute(self, force: bool = False) -> CollectionReport:
        """`force` consulta aunque la bolsa esté cerrada (p. ej., para guardar el cierre)."""
        report = CollectionReport(market_open=self._market_hours.is_open(self._clock.now()))
        self._collect_exchange_rate(report)
        if report.market_open or force:
            self._collect_quotation(report)
        return report

    def _collect_exchange_rate(self, report: CollectionReport) -> None:
        # El BCRP publica una vez al día: no tiene sentido consultarlo cada minuto
        current = self._repository.exchange_rate_on(self._clock.today())
        if current is not None and current.rated_on == self._clock.today():
            return
        try:
            rate = _with_retries(self._exchange_rates.fetch_latest)
        except SourceUnavailableError as error:
            self._register_issue(report, f"Tipo de cambio: {error}")
            return
        self._repository.add_exchange_rate(rate)
        report.exchange_rate_saved = True

    def _collect_quotation(self, report: CollectionReport) -> None:
        quotes = self._fetch_all_sources(report)
        try:
            result = self._consensus.consolidate(quotes)
            report.sources_discarded = list(result.discarded)
            for name in result.discarded:
                self._register_issue(report, f"{name}: se aleja de las demás fuentes; se descarta")
            self._validator.validate(result.quote, self._repository.last_live_quote())
        except MarketError as error:
            # No se publica nada: el caficultor sigue viendo el último valor válido
            self._register_issue(report, f"Cotización: {error}")
            return
        self._save(result.quote)
        report.quotation_saved = True

    def _fetch_all_sources(self, report: CollectionReport) -> list[LiveQuote]:
        quotes: list[LiveQuote] = []
        for source in self._sources:
            try:
                quotes.append(source.fetch_latest())
                report.sources_ok.append(source.name)
            except SourceUnavailableError as error:
                # Una web caída no detiene la recolección: se sigue con las demás
                self._register_issue(report, f"{source.name}: {error}")
        return quotes

    def _save(self, quote: LiveQuote) -> None:
        self._repository.add_live_quote(quote)
        # El último precio del día queda como cierre diario (histórico y pronóstico)
        self._repository.save_daily_close(
            Quotation(
                cents_per_pound=quote.cents_per_pound,
                quoted_on=MarketHours.trading_day(quote.quoted_at),
                source=", ".join(quote.sources),
            )
        )

    @staticmethod
    def _register_issue(report: CollectionReport, issue: str) -> None:
        logger.warning("Incidente en la recolección: %s", issue)
        report.issues.append(issue)


def _with_retries(fetch: Callable[[], T]) -> T:
    """Reintenta una consulta a una fuente externa hasta MAX_ATTEMPTS veces."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fetch()
        except SourceUnavailableError:
            if attempt == MAX_ATTEMPTS:
                raise
            logger.info("Reintentando la fuente (intento %s de %s)", attempt + 1, MAX_ATTEMPTS)
    raise AssertionError("unreachable")  # pragma: no cover
