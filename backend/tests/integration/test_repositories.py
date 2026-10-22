from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from forecasting.domain.forecast import Forecast
from forecasting.infrastructure.persistence.sqlalchemy_forecast_repository import (
    SqlAlchemyForecastRepository,
)
from identity.domain.invitation_code import InvitationCode
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import Consent, Role, User
from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
    SqlAlchemyUserRepository,
)
from market.domain.local_price import CoffeeType, LocalPriceObservation
from market.domain.quotation import LiveQuote
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from orchestration.domain.trace import AgentTrace
from orchestration.infrastructure.persistence.sqlalchemy_trace_repository import (
    SqlAlchemyTraceRepository,
)
from orchestration.infrastructure.persistence.tables import agent_traces
from shared.domain.agent_message import Performative
from tests.fakes import LIMA, quotation, rate

NOW = datetime(2026, 11, 4, 9, 0)


def test_user_is_saved_and_code_redeemed_together(sessions: sessionmaker[Session]) -> None:
    codes = SqlAlchemyInvitationCodeRepository(sessions)
    codes.add_many(["JAEN-ABC234"])
    users = SqlAlchemyUserRepository(sessions)
    user = User("u-1", PhoneNumber("987654321"), "hash", Consent("2026-10", NOW), NOW)

    users.add(user, InvitationCode("JAEN-ABC234").redeem(user.id, NOW))

    assert users.get_by_phone(PhoneNumber("987654321")) == user
    stored_code = codes.get("JAEN-ABC234")
    assert stored_code is not None and stored_code.used_by == "u-1"


def test_admin_is_saved_without_invitation_code(sessions: sessionmaker[Session]) -> None:
    users = SqlAlchemyUserRepository(sessions)
    admin = User.create_admin(PhoneNumber("911111111"), "hash", NOW)

    users.add(admin, None)

    stored = users.get_by_phone(PhoneNumber("911111111"))
    assert stored is not None and stored.role is Role.ADMIN


def test_local_prices_keep_time_zone_type_and_order(sessions: sessionmaker[Session]) -> None:
    prices = SqlAlchemyPriceRepository(sessions)
    old = LocalPriceObservation(
        datetime(2026, 11, 3, 9, 0, tzinfo=LIMA),
        "Coop. A",
        CoffeeType.CONVENTIONAL,
        Decimal("900"),
        Decimal("1140"),
    )
    new = LocalPriceObservation(
        datetime(2026, 11, 4, 9, 0, tzinfo=LIMA),
        "Coop. B",
        CoffeeType.ORGANIC,
        Decimal("1000"),
        Decimal("1150.5"),
    )
    prices.add_local_observation(old)
    prices.add_local_observation(new)

    assert prices.local_observations_since(old.observed_at) == [new, old]
    assert prices.local_observations_since(new.observed_at) == [new]


def test_price_repository_orders_and_finds_rate_in_force(sessions: sessionmaker[Session]) -> None:
    prices = SqlAlchemyPriceRepository(sessions)
    prices.save_daily_close(quotation("300", date(2026, 11, 3)))
    prices.save_daily_close(quotation("304", date(2026, 11, 4)))
    prices.save_daily_close(quotation("305", date(2026, 11, 4)))  # reemplaza el cierre del día
    prices.add_exchange_rate(rate("3.70", date(2026, 11, 1)))
    prices.add_exchange_rate(rate("3.75", date(2026, 11, 1)))  # reemplaza el del mismo día

    assert [q.cents_per_pound for q in prices.last_quotations(2)] == [
        Decimal("305"),
        Decimal("300"),
    ]
    found = prices.exchange_rate_on(date(2026, 11, 4))
    assert found is not None and found.soles_per_dollar == Decimal("3.75")
    assert prices.exchange_rate_on(date(2026, 10, 1)) is None
    assert len(prices.quotations_since(date(2026, 11, 4))) == 1


def test_live_quotes_keep_time_zone_and_sources(sessions: sessionmaker[Session]) -> None:
    prices = SqlAlchemyPriceRepository(sessions)
    first = LiveQuote(Decimal("300"), datetime(2026, 11, 4, 9, 0, tzinfo=LIMA), ("Yahoo", "Stooq"))
    second = LiveQuote(Decimal("301"), datetime(2026, 11, 4, 9, 1, tzinfo=LIMA), ("Yahoo",))
    prices.add_live_quote(second)
    prices.add_live_quote(first)

    last = prices.last_live_quote()
    between = prices.live_quotes_between(first.quoted_at, second.quoted_at + timedelta(seconds=1))

    assert last == second  # misma hora (en UTC) y mismas fuentes
    assert [q.cents_per_pound for q in between] == [Decimal("300"), Decimal("301")]
    assert between[0].sources == ("Yahoo", "Stooq")


def test_forecast_round_trip(sessions: sessionmaker[Session]) -> None:
    repository = SqlAlchemyForecastRepository(sessions)
    forecast = Forecast.from_predictions(
        date(2026, 11, 4), "elm", 3.5, [date(2026, 11, 5)], [1150.0]
    )

    repository.save(forecast)

    assert repository.latest() == forecast


def test_trace_is_persisted(sessions: sessionmaker[Session]) -> None:
    trace = AgentTrace(uuid4(), "api", "analyst", "get_live_price", Performative.INFORM, 12, NOW)

    SqlAlchemyTraceRepository(sessions).add(trace)

    with sessions() as session:
        row = session.execute(select(agent_traces)).one()
    assert (row.receiver, row.result, row.duration_ms) == ("analyst", "INFORM", 12)
