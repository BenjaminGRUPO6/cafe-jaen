from datetime import datetime, time, timedelta

from market.domain.live_price import HistoryPoint, IntradayPoint
from market.domain.market_hours import NEW_YORK, MarketHours
from market.domain.ports.price_repository import PriceRepository
from market.domain.quintal_price import PriceConverter
from shared.domain.ports.clock import Clock


class GetPriceHistory:
    """HU04: gráfico tipo bolsa: hoy minuto a minuto y cierres de los últimos N días."""

    def __init__(
        self, repository: PriceRepository, converter: PriceConverter, clock: Clock
    ) -> None:
        self._repository = repository
        self._converter = converter
        self._clock = clock

    def intraday(self) -> list[IntradayPoint]:
        """Cotizaciones del último día de negociación con datos (hoy, o el último hábil)."""
        last = self._repository.last_live_quote()
        if last is None:
            return []
        day = MarketHours.trading_day(last.quoted_at)
        start = datetime.combine(day, time.min, tzinfo=NEW_YORK)
        quotes = self._repository.live_quotes_between(start, start + timedelta(days=1))
        rate = self._repository.exchange_rate_on(self._clock.today())
        if rate is None:
            return []
        return [
            IntradayPoint(
                q.quoted_at, self._converter.to_quintal(q.cents_per_pound, rate.soles_per_dollar)
            )
            for q in quotes
        ]

    def daily(self, days: int) -> list[HistoryPoint]:
        since = self._clock.today() - timedelta(days=days)
        quotations = self._repository.quotations_since(since)
        # Tipo de cambio vigente al inicio del periodo + los publicados después
        rate_at_start = self._repository.exchange_rate_on(since)
        rates = ([rate_at_start] if rate_at_start else []) + [
            r for r in self._repository.exchange_rates_since(since) if r != rate_at_start
        ]

        points: list[HistoryPoint] = []
        rate_index = -1
        for quotation in quotations:
            # Avanza hasta el último tipo de cambio publicado hasta la fecha de la cotización
            while (
                rate_index + 1 < len(rates)
                and rates[rate_index + 1].rated_on <= quotation.quoted_on
            ):
                rate_index += 1
            if rate_index < 0:
                continue
            price = self._converter.to_quintal(
                quotation.cents_per_pound, rates[rate_index].soles_per_dollar
            )
            points.append(HistoryPoint(quotation.quoted_on, price))
        return points
