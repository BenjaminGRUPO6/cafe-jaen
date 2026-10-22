from datetime import timedelta

from market.domain.errors import PriceNotAvailableError
from market.domain.live_price import LivePrice
from market.domain.local_price import LocalPriceEstimator
from market.domain.market_hours import MarketHours
from market.domain.ports.price_repository import PriceRepository
from market.domain.quintal_price import PriceConverter, QuintalPrice
from market.domain.quotation import LiveQuote, Quotation
from shared.domain.ports.clock import Clock


class GetLivePrice:
    """HU03: precio en vivo en ¢USD/lb y S/ por quintal y su variación frente al cierre anterior."""

    def __init__(
        self,
        repository: PriceRepository,
        converter: PriceConverter,
        market_hours: MarketHours,
        clock: Clock,
        stale_after: timedelta = timedelta(minutes=20),
        estimator: LocalPriceEstimator | None = None,
    ) -> None:
        self._repository = repository
        self._converter = converter
        self._market_hours = market_hours
        self._clock = clock
        self._stale_after = stale_after
        self._estimator = estimator or LocalPriceEstimator()

    def execute(self) -> LivePrice:
        quote = self._latest_quote()
        rate = self._repository.exchange_rate_on(self._clock.today())
        if rate is None:
            raise PriceNotAvailableError()
        now = self._clock.now()
        market_open = self._market_hours.is_open(now)
        price = self._converter.to_quintal(quote.cents_per_pound, rate.soles_per_dollar)
        observations = self._repository.local_observations_since(now - self._estimator.window)
        return LivePrice(
            quoted_at=quote.quoted_at,
            cents_per_pound=quote.cents_per_pound,
            price=price,
            previous_close=self._previous_close(quote),
            sources=tuple(dict.fromkeys([*quote.sources, rate.source])),  # sin repetir
            market_open=market_open,
            stale=market_open and now - quote.quoted_at > self._stale_after,
            local_estimates=tuple(self._estimator.estimate(price.soles, observations)),
        )

    def _latest_quote(self) -> LiveQuote:
        live = self._repository.last_live_quote()
        if live is not None:
            return live
        # Sin cotizaciones en vivo (p. ej., solo se cargó el histórico) se usa el último cierre
        closes = self._repository.last_quotations(limit=1)
        if not closes:
            raise PriceNotAvailableError()
        close = closes[0]
        return LiveQuote(
            close.cents_per_pound, self._market_hours.close_of(close.quoted_on), (close.source,)
        )

    def _previous_close(self, quote: LiveQuote) -> QuintalPrice | None:
        trading_day = MarketHours.trading_day(quote.quoted_at)
        previous = next(
            (q for q in self._repository.last_quotations(limit=5) if q.quoted_on < trading_day),
            None,
        )
        return self._convert(previous) if previous else None

    def _convert(self, quotation: Quotation) -> QuintalPrice | None:
        rate = self._repository.exchange_rate_on(quotation.quoted_on)
        if rate is None:
            return None
        return self._converter.to_quintal(quotation.cents_per_pound, rate.soles_per_dollar)
