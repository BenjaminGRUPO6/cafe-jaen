"""PA-12-1 a PA-12-3 (HU12): precio estimado en Jaén a partir de la bolsa."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from market.application.get_live_price import GetLivePrice
from market.application.record_local_price import RecordLocalPrice, RecordLocalPriceCommand
from market.domain.errors import InvalidLocalPriceError
from market.domain.local_price import CoffeeType, LocalPriceEstimator, LocalPriceObservation
from market.domain.market_hours import MarketHours
from market.domain.quintal_price import PriceConverter
from tests.fakes import LIMA, FixedClock, InMemoryPriceRepository, live, rate

NOW = datetime(2026, 11, 4, 9, 0, tzinfo=LIMA)
CLOCK = FixedClock(NOW)


def seen(paid: str, exchange: str, coffee: CoffeeType = CoffeeType.CONVENTIONAL, days_ago: int = 0):  # type: ignore[no-untyped-def]
    return LocalPriceObservation(
        NOW - timedelta(days=days_ago), "Coop. A", coffee, Decimal(paid), Decimal(exchange)
    )


def test_estimate_uses_median_ratio_of_each_coffee_type() -> None:
    observations = [
        seen("900", "1140"),  # 78,9 %
        seen("880", "1125", days_ago=1),  # 78,2 %
        seen("910", "1150", days_ago=2),  # 79,1 %
        seen("1000", "1140", CoffeeType.ORGANIC),  # 87,7 %
    ]

    estimates = LocalPriceEstimator().estimate(Decimal("1200"), observations)

    conventional, organic = estimates
    assert conventional.coffee_type is CoffeeType.CONVENTIONAL
    assert conventional.ratio == Decimal("0.7895")
    assert conventional.estimated_soles == Decimal("947.37")  # 1200 × 78,947 %
    assert (conventional.observations, conventional.few_data) == (3, False)
    assert organic.observations == 1 and organic.few_data
    assert all(
        e.coffee_type is not CoffeeType.SPECIALTY for e in estimates
    )  # sin datos: no se inventa


def test_one_odd_price_does_not_move_the_median() -> None:
    observations = [seen("900", "1140"), seen("905", "1140"), seen("1300", "1140")]

    (estimate,) = LocalPriceEstimator().estimate(Decimal("1140"), observations)

    assert estimate.estimated_soles == Decimal("905.00")


@pytest.mark.parametrize(
    ("cooperative", "paid"),
    [("Coop. A", "90"), ("Coop. A", "0"), ("  ", "900"), ("Coop. A", "1500")],
)
def test_rejects_prices_that_look_mistyped(cooperative: str, paid: str) -> None:
    with pytest.raises(InvalidLocalPriceError):
        LocalPriceObservation(
            NOW, cooperative, CoffeeType.CONVENTIONAL, Decimal(paid), Decimal("1140")
        )


@pytest.fixture
def repository() -> InMemoryPriceRepository:
    repo = InMemoryPriceRepository()
    repo.add_exchange_rate(rate("3.75", NOW.date()))
    repo.add_live_quote(live("300", NOW - timedelta(minutes=5)))  # S/ 1140,89
    return repo


def test_record_saves_price_with_exchange_of_that_moment(
    repository: InMemoryPriceRepository,
) -> None:
    live_price = GetLivePrice(repository, PriceConverter(), MarketHours(), CLOCK)
    record = RecordLocalPrice(repository, live_price, CLOCK)

    saved = record.execute(RecordLocalPriceCommand(" Coop. A ", "organico", "1000"))

    assert saved.cooperative == "Coop. A" and saved.coffee_type is CoffeeType.ORGANIC
    assert saved.exchange_soles == Decimal("1140.89")
    assert record.recent() == [saved]


@pytest.mark.parametrize(("coffee", "paid"), [("arabico", "900"), ("convencional", "novecientos")])
def test_record_rejects_unknown_type_or_amount(
    repository: InMemoryPriceRepository, coffee: str, paid: str
) -> None:
    live_price = GetLivePrice(repository, PriceConverter(), MarketHours(), CLOCK)

    with pytest.raises(InvalidLocalPriceError):
        RecordLocalPrice(repository, live_price, CLOCK).execute(
            RecordLocalPriceCommand("Coop. A", coffee, paid)
        )


def test_live_price_estimate_moves_with_the_exchange_and_ignores_old_prices(
    repository: InMemoryPriceRepository,
) -> None:
    repository.add_local_observation(seen("900", "1140"))
    repository.add_local_observation(seen("500", "1140", days_ago=40))  # fuera de los 30 días
    repository.add_live_quote(live("310", NOW - timedelta(minutes=1)))  # la bolsa sube

    price = GetLivePrice(repository, PriceConverter(), MarketHours(), CLOCK).execute()

    (estimate,) = price.local_estimates
    assert estimate.observations == 1
    # 900 / 1140 = 78,947 % de la bolsa actual (S/ 1178,92 con 310 ¢/lb)
    expected = price.price.soles * Decimal(900) / Decimal(1140)
    assert estimate.estimated_soles == expected.quantize(Decimal("0.01"))
