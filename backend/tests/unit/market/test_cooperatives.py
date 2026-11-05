"""Catálogo de cooperativas y corrección de precios anotados (pantalla «Equipo»)."""

from datetime import timedelta
from decimal import Decimal

import pytest

from market.application.correct_local_price import CorrectLocalPrice
from market.application.get_live_price import GetLivePrice
from market.application.get_price_log import GetPriceLog
from market.application.manage_cooperatives import CooperativeData, ManageCooperatives, Removal
from market.application.record_local_price import RecordLocalPrice, RecordLocalPriceCommand
from market.domain.cooperative import Cooperative
from market.domain.errors import InvalidCooperativeError, InvalidLocalPriceError, NotFoundError
from market.domain.local_price import CoffeeType, LocalPriceEstimator, LocalPriceObservation
from market.domain.market_hours import MarketHours
from market.domain.quintal_price import PriceConverter
from tests.fakes import (
    FixedClock,
    InMemoryCooperativeRepository,
    InMemoryPriceRepository,
    live,
    rate,
)

CLOCK = FixedClock()
NOW = CLOCK.now()


@pytest.mark.parametrize(("name", "website"), [("X", None), ("Coop. Bien", "www.sin-protocolo.pe")])
def test_cooperative_rejects_invalid_data(name: str, website: str | None) -> None:
    with pytest.raises(InvalidCooperativeError):
        Cooperative.create(name, "Jaén", website)


def test_create_trims_and_rejects_duplicates_ignoring_case() -> None:
    manage = ManageCooperatives(InMemoryCooperativeRepository("CENFROCAFE"))

    created = manage.create(CooperativeData("  Sol & Café ", " ", " https://solcafe.pe "))

    assert (created.name, created.location, created.website) == (
        "Sol & Café",
        "Jaén",
        "https://solcafe.pe",
    )
    with pytest.raises(InvalidCooperativeError, match="ya está en el catálogo"):
        manage.create(CooperativeData("cenfrocafe"))


def test_rename_keeps_prices_linked() -> None:
    repository = InMemoryCooperativeRepository("Coop A")
    manage = ManageCooperatives(repository)

    edited = manage.update(1, CooperativeData("Cooperativa A", "Jaén", None, active=True))

    assert edited.name == "Cooperativa A"
    assert repository.renamed == [("Coop A", "Cooperativa A")]


def test_remove_archives_when_it_has_prices_and_deletes_otherwise() -> None:
    repository = InMemoryCooperativeRepository("Con precios", "Sin precios")
    repository.with_prices.add("Con precios")
    manage = ManageCooperatives(repository)

    assert manage.remove(1) is Removal.ARCHIVED
    assert manage.remove(2) is Removal.DELETED
    assert [(c.name, c.active) for c in manage.list()] == [("Con precios", False)]
    with pytest.raises(NotFoundError):
        manage.remove(2)


@pytest.fixture
def prices() -> InMemoryPriceRepository:
    repository = InMemoryPriceRepository()
    repository.add_exchange_rate(rate("3.75", NOW.date()))
    repository.add_live_quote(live("300", NOW - timedelta(minutes=5)))  # S/ 1140,89
    return repository


def test_only_active_catalog_cooperatives_can_receive_prices(
    prices: InMemoryPriceRepository,
) -> None:
    catalog = InMemoryCooperativeRepository("CENFROCAFE", "Archivada")
    catalog.update(catalog.items[2].edit("Archivada", "Jaén", None, False), "Archivada")
    record = RecordLocalPrice(
        prices, GetLivePrice(prices, PriceConverter(), MarketHours(), CLOCK), catalog, CLOCK
    )

    saved = record.execute(RecordLocalPriceCommand("cenfrocafe", "convencional", "900"))

    assert saved.cooperative == "CENFROCAFE" and saved.id == 1  # nombre tal como en el catálogo
    for name in ("No existe", "Archivada"):
        with pytest.raises(InvalidLocalPriceError, match="catálogo"):
            record.execute(RecordLocalPriceCommand(name, "convencional", "900"))


def observation(paid: str) -> LocalPriceObservation:
    return LocalPriceObservation(
        NOW, "Coop. A", CoffeeType.CONVENTIONAL, Decimal(paid), Decimal("1140")
    )


def test_correct_recomputes_ratio_with_the_original_exchange(
    prices: InMemoryPriceRepository,
) -> None:
    saved = prices.add_local_observation(observation("900"))
    correct = CorrectLocalPrice(prices)

    corrected = correct.edit(saved.id or 0, "1000")

    assert corrected.ratio == Decimal("1000") / Decimal("1140")
    assert prices.local[0].paid_soles == Decimal("1000")
    with pytest.raises(InvalidLocalPriceError):
        correct.edit(saved.id or 0, "100")  # 9 % de la bolsa: error al escribir


def test_delete_price_and_missing_ids(prices: InMemoryPriceRepository) -> None:
    saved = prices.add_local_observation(observation("900"))
    correct = CorrectLocalPrice(prices)

    correct.delete(saved.id or 0)

    assert prices.local == []
    with pytest.raises(NotFoundError):
        correct.delete(saved.id or 0)
    with pytest.raises(NotFoundError):
        correct.edit(99, "900")


def test_price_log_shows_each_quote_in_soles_and_per_coffee_type(
    prices: InMemoryPriceRepository,
) -> None:
    prices.add_live_quote(live("310", NOW - timedelta(minutes=1)))
    prices.add_live_quote(live("200", NOW - timedelta(days=2)))  # otro día
    prices.add_local_observation(observation("912"))  # 912 / 1140 = 80 % de la bolsa

    entries = GetPriceLog(prices, PriceConverter(), LocalPriceEstimator(), CLOCK).execute().entries

    assert [e.cents_per_pound for e in entries] == [Decimal("310"), Decimal("300")]
    assert all(e.published and e.readings == () for e in entries)  # sin detalle de fuentes
    assert entries[1].price_soles == Decimal("1140.89")
    assert entries[1].local_soles == {CoffeeType.CONVENTIONAL: Decimal("912.71")}
    assert CoffeeType.ORGANIC not in entries[0].local_soles  # sin precios anotados: sin estimado
