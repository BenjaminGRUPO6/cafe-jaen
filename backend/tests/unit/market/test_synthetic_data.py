"""Precios sintéticos de cooperativas para la demostración: claros, abundantes y borrables."""

from datetime import timedelta
from decimal import Decimal

import pytest

from market.application.manage_synthetic_data import ManageSyntheticData, NoRealExchangeError
from market.domain.cooperative import Cooperative
from market.domain.local_price import (
    MAX_RATIO,
    MIN_RATIO,
    CoffeeType,
    LocalPriceEstimator,
    LocalPriceObservation,
    is_synthetic,
)
from market.domain.quintal_price import PriceConverter
from market.domain.quotation import ExchangeRate, Quotation
from market.domain.synthetic_data import ExchangeDay, generate_observations, synthetic_names
from tests.fakes import FixedClock, InMemoryCooperativeRepository, InMemoryPriceRepository

CLOCK = FixedClock()
TODAY = CLOCK.today()


def real_market(prices: InMemoryPriceRepository, days: int = 60) -> None:
    """Histórico «real» de prueba: cierres diarios y tipo de cambio."""
    for offset in range(days):
        day = TODAY - timedelta(days=offset)
        if day.weekday() < 5:
            prices.save_daily_close(Quotation(Decimal("300"), day, "Yahoo Finance"))
            prices.add_exchange_rate(ExchangeRate(Decimal("3.75"), day, "BCRP"))


def manager(
    prices: InMemoryPriceRepository, coops: InMemoryCooperativeRepository
) -> ManageSyntheticData:
    return ManageSyntheticData(prices, coops, PriceConverter(), CLOCK)


def test_names_say_they_are_synthetic() -> None:
    names = synthetic_names()
    assert names[0] == "Cooperativa JAENPERU sintético A"
    assert len(names) == 6
    assert all(is_synthetic(name) for name in names)
    assert not is_synthetic("CENFROCAFE – Central Fronteriza del Norte de Cafetaleros")


def test_generated_prices_follow_the_real_exchange_and_stay_in_range() -> None:
    days = [ExchangeDay(CLOCK.now() - timedelta(days=i), Decimal("1140.00")) for i in range(40)]

    observations = generate_observations(days, synthetic_names(), seed=7)

    assert len(observations) > 500  # mucha data: 6 cooperativas × 3 tipos × 40 días (≈85 %)
    assert {o.coffee_type for o in observations} == set(CoffeeType)
    assert all(o.exchange_soles == Decimal("1140.00") for o in observations)
    assert all(MIN_RATIO <= o.ratio <= MAX_RATIO for o in observations)
    organic = [o.ratio for o in observations if o.coffee_type is CoffeeType.ORGANIC]
    conventional = [o.ratio for o in observations if o.coffee_type is CoffeeType.CONVENTIONAL]
    assert sum(organic) / len(organic) > sum(conventional) / len(conventional)


def test_load_replaces_previous_synthetic_data_and_keeps_real_prices() -> None:
    prices, coops = InMemoryPriceRepository(), InMemoryCooperativeRepository()
    real_market(prices)
    coops.add(Cooperative.create("Cooperativa Agraria Café del Norte", "Jaén", None))
    prices.add_local_observation(
        LocalPriceObservation(
            CLOCK.now(),
            "Cooperativa Agraria Café del Norte",
            CoffeeType.CONVENTIONAL,
            Decimal("820"),
            Decimal("1140"),
        )
    )

    first = manager(prices, coops).load()
    second = manager(prices, coops).load()

    assert first.cooperatives == second.cooperatives == 6
    # Al volver a cargar se reemplazan (no se suman): solo quedan los de la segunda carga
    synthetic = [o for o in prices.local if is_synthetic(o.cooperative)]
    assert len(synthetic) == second.observations
    assert 300 < second.observations < first.observations * 1.3
    real = [o for o in prices.local if not is_synthetic(o.cooperative)]
    assert [o.cooperative for o in real] == ["Cooperativa Agraria Café del Norte"]


def test_remove_deletes_only_synthetic_cooperatives_and_prices() -> None:
    prices, coops = InMemoryPriceRepository(), InMemoryCooperativeRepository()
    real_market(prices)
    coops.add(Cooperative.create("CENFROCAFE", "Jaén", None))
    manager(prices, coops).load()

    removed = manager(prices, coops).remove()

    assert removed.observations > 300
    assert [c.name for c in coops.all()] == ["CENFROCAFE"]
    assert prices.local == []
    assert manager(prices, coops).status().observations == 0


def test_without_real_exchange_nothing_is_invented() -> None:
    with pytest.raises(NoRealExchangeError):
        manager(InMemoryPriceRepository(), InMemoryCooperativeRepository()).load()


def test_estimate_tells_how_many_prices_are_synthetic() -> None:
    def obs(name: str) -> LocalPriceObservation:
        return LocalPriceObservation(
            CLOCK.now(), name, CoffeeType.CONVENTIONAL, Decimal("820"), Decimal("1140")
        )

    (estimate,) = LocalPriceEstimator().estimate(
        Decimal("1140"), [obs("CENFROCAFE"), obs("Cooperativa JAENPERU sintético A")]
    )

    assert (estimate.observations, estimate.synthetic) == (2, 1)
