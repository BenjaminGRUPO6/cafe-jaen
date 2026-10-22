from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Row, delete, insert, select
from sqlalchemy.orm import Session, sessionmaker

from market.domain.local_price import CoffeeType, LocalPriceObservation
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from market.infrastructure.persistence.tables import (
    exchange_rates,
    live_quotes,
    local_price_observations,
    quotations,
)

SOURCE_SEPARATOR = ", "


class SqlAlchemyPriceRepository:
    """Implementa PriceRepository. Las horas se guardan en UTC."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    # ---------------------------------------------------------------- en vivo
    def add_live_quote(self, quote: LiveQuote) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                insert(live_quotes).values(
                    quoted_at=quote.quoted_at.astimezone(UTC),
                    cents_per_pound=quote.cents_per_pound,
                    sources=SOURCE_SEPARATOR.join(quote.sources),
                )
            )

    def last_live_quote(self) -> LiveQuote | None:
        query = select(live_quotes).order_by(live_quotes.c.quoted_at.desc()).limit(1)
        with self._sessions() as session:
            row = session.execute(query).first()
        return _to_live_quote(row) if row else None

    def live_quotes_between(self, start: datetime, end: datetime) -> list[LiveQuote]:
        query = (
            select(live_quotes)
            .where(live_quotes.c.quoted_at >= start.astimezone(UTC))
            .where(live_quotes.c.quoted_at < end.astimezone(UTC))
            .order_by(live_quotes.c.quoted_at)
        )
        with self._sessions() as session:
            return [_to_live_quote(row) for row in session.execute(query)]

    # ---------------------------------------------------------------- cierres diarios
    def save_daily_close(self, quotation: Quotation) -> None:
        with self._sessions() as session, session.begin():
            session.execute(delete(quotations).where(quotations.c.quoted_on == quotation.quoted_on))
            session.execute(
                insert(quotations).values(
                    quoted_on=quotation.quoted_on,
                    cents_per_pound=quotation.cents_per_pound,
                    source=quotation.source,
                )
            )

    def last_quotations(self, limit: int) -> list[Quotation]:
        query = select(quotations).order_by(quotations.c.quoted_on.desc()).limit(limit)
        with self._sessions() as session:
            return [_to_quotation(row) for row in session.execute(query)]

    def quotations_since(self, day: date) -> list[Quotation]:
        query = (
            select(quotations).where(quotations.c.quoted_on >= day).order_by(quotations.c.quoted_on)
        )
        with self._sessions() as session:
            return [_to_quotation(row) for row in session.execute(query)]

    # ---------------------------------------------------------------- cooperativas (HU12)
    def add_local_observation(self, observation: LocalPriceObservation) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                insert(local_price_observations).values(
                    observed_at=observation.observed_at.astimezone(UTC),
                    cooperative=observation.cooperative,
                    coffee_type=observation.coffee_type.value,
                    paid_soles=observation.paid_soles,
                    exchange_soles=observation.exchange_soles,
                )
            )

    def local_observations_since(self, moment: datetime) -> list[LocalPriceObservation]:
        table = local_price_observations
        query = (
            select(table)
            .where(table.c.observed_at >= moment.astimezone(UTC))
            .order_by(table.c.observed_at.desc())
        )
        with self._sessions() as session:
            return [
                LocalPriceObservation(
                    _utc(row.observed_at),
                    row.cooperative,
                    CoffeeType(row.coffee_type),
                    Decimal(row.paid_soles),
                    Decimal(row.exchange_soles),
                )
                for row in session.execute(query)
            ]

    # ---------------------------------------------------------------- tipo de cambio
    def add_exchange_rate(self, rate: ExchangeRate) -> None:
        # Reemplaza el valor del día si ya existía (el BCRP puede corregirlo)
        with self._sessions() as session, session.begin():
            session.execute(
                delete(exchange_rates).where(exchange_rates.c.rated_on == rate.rated_on)
            )
            session.execute(
                insert(exchange_rates).values(
                    rated_on=rate.rated_on,
                    soles_per_dollar=rate.soles_per_dollar,
                    source=rate.source,
                )
            )

    def exchange_rate_on(self, day: date) -> ExchangeRate | None:
        query = (
            select(exchange_rates)
            .where(exchange_rates.c.rated_on <= day)
            .order_by(exchange_rates.c.rated_on.desc())
            .limit(1)
        )
        with self._sessions() as session:
            row = session.execute(query).first()
        return _to_rate(row) if row else None

    def exchange_rates_since(self, day: date) -> list[ExchangeRate]:
        query = (
            select(exchange_rates)
            .where(exchange_rates.c.rated_on >= day)
            .order_by(exchange_rates.c.rated_on)
        )
        with self._sessions() as session:
            return [_to_rate(row) for row in session.execute(query)]


def _utc(moment: datetime) -> datetime:
    # SQLite no guarda la zona horaria: se vuelve a poner UTC al leer
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def _to_live_quote(row: Row) -> LiveQuote:  # type: ignore[type-arg]
    return LiveQuote(
        Decimal(row.cents_per_pound),
        _utc(row.quoted_at),
        tuple(row.sources.split(SOURCE_SEPARATOR)),
    )


def _to_quotation(row: Row) -> Quotation:  # type: ignore[type-arg]
    return Quotation(Decimal(row.cents_per_pound), row.quoted_on, row.source)


def _to_rate(row: Row) -> ExchangeRate:  # type: ignore[type-arg]
    return ExchangeRate(Decimal(row.soles_per_dollar), row.rated_on, row.source)
