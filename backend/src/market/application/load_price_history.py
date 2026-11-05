import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta

from market.domain.errors import SourceUnavailableError
from market.domain.ports.price_repository import PriceRepository
from market.domain.ports.sources import DailyHistorySource, ExchangeRateHistoryProvider
from shared.domain.ports.clock import Clock

logger = logging.getLogger(__name__)

# Con menos cierres del último año, el gráfico de 90 días y el pronóstico no tienen insumo
MIN_RECENT_CLOSES = 150
RECENT = timedelta(days=365)


@dataclass
class HistoryReport:
    closes_saved: int = 0
    rates_saved: int = 0
    source: str | None = None  # web de la que salieron los cierres
    skipped: bool = False  # ya había histórico suficiente
    issues: list[str] = field(default_factory=list)


class LoadPriceHistory:
    """Carga el histórico REAL de cierres diarios y del tipo de cambio (gráfico y pronóstico).

    Prueba las webs en orden (Yahoo Finance y, si falla, Stooq) y pide el tipo de cambio al
    BCRP año por año. Es idempotente: si ya hay histórico suficiente, no hace nada; nunca
    reemplaza un cierre que ya existe.
    """

    def __init__(
        self,
        sources: Sequence[DailyHistorySource],
        rates: ExchangeRateHistoryProvider,
        repository: PriceRepository,
        clock: Clock,
    ) -> None:
        self._sources = sources
        self._rates = rates
        self._repository = repository
        self._clock = clock

    def execute(self, years: int, force: bool = False) -> HistoryReport:
        today = self._clock.today()
        report = HistoryReport()
        recent = self._repository.quotations_since(today - RECENT)
        if len(recent) >= MIN_RECENT_CLOSES and not force:
            report.skipped = True
            return report
        start = today - timedelta(days=365 * years)
        self._load_closes(start, report)
        self._load_rates(start, today, report)
        return report

    def _load_closes(self, start: date, report: HistoryReport) -> None:
        existing = {q.quoted_on for q in self._repository.quotations_since(start)}
        for source in self._sources:
            try:
                history = source.fetch_daily_history(start)
            except SourceUnavailableError as error:
                report.issues.append(f"{source.name}: {error}")
                logger.warning("Histórico: %s no respondió (%s)", source.name, error)
                continue
            for quotation in history:
                if quotation.quoted_on not in existing:
                    self._repository.save_daily_close(quotation)
                    report.closes_saved += 1
            report.source = source.name
            return  # basta una web que responda
        report.issues.append("Ninguna web entregó el histórico de cierres")

    def _load_rates(self, start: date, today: date, report: HistoryReport) -> None:
        # El BCRP limita el tamaño de cada consulta: se pide año por año
        for year in range(start.year, today.year + 1):
            chunk_start = max(start, date(year, 1, 1))
            chunk_end = min(today, date(year, 12, 31))
            try:
                rates = self._rates.fetch_history(chunk_start, chunk_end)
            except SourceUnavailableError as error:
                report.issues.append(f"BCRP {year}: {error}")
                continue
            for rate in rates:
                self._repository.add_exchange_rate(rate)
                report.rates_saved += 1
