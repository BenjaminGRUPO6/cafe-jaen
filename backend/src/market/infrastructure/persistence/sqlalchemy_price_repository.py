from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Row, delete, func, insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from market.domain.local_price import CoffeeType, LocalPriceObservation
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from market.domain.source_reading import (
    CollectionOutcome,
    PriceCollection,
    ReadingStatus,
    SourceReading,
)
from market.infrastructure.persistence.tables import (
    exchange_rates,
    live_exchange_rates,
    live_quotes,
    local_price_observations,
    price_collections,
    quotations,
    source_readings,
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

    # ---------------------------------------------------------------- registro de consultas
    def add_collection(self, collection: PriceCollection) -> None:
        with self._sessions() as session, session.begin():
            collection_id = session.execute(
                insert(price_collections)
                .values(
                    collected_at=collection.collected_at.astimezone(UTC),
                    median_cents=collection.median_cents,
                    published_cents=collection.published_cents,
                    published_quoted_at=_to_utc(collection.published_quoted_at),
                    outcome=collection.outcome.value,
                    detail=collection.detail,
                )
                .returning(price_collections.c.id)
            ).scalar_one()
            if collection.readings:
                session.execute(
                    insert(source_readings),
                    [
                        {
                            "collection_id": collection_id,
                            "source": r.source[:40],
                            "status": r.status.value,
                            "cents_per_pound": r.cents_per_pound,
                            "quoted_at": _to_utc(r.quoted_at),
                            "deviation_pct": r.deviation_pct,
                            "detail": r.detail,
                            "has_exchange_time": r.has_exchange_time,
                        }
                        for r in collection.readings
                    ],
                )

    def collections_between(self, start: datetime, end: datetime) -> list[PriceCollection]:
        query = (
            select(price_collections)
            .where(price_collections.c.collected_at >= start.astimezone(UTC))
            .where(price_collections.c.collected_at < end.astimezone(UTC))
            .order_by(price_collections.c.collected_at, price_collections.c.id)
        )
        with self._sessions() as session:
            rows = session.execute(query).all()
            ids = [row.id for row in rows]
            readings: dict[int, list[SourceReading]] = {i: [] for i in ids}
            if ids:
                reading_rows = session.execute(
                    select(source_readings)
                    .where(source_readings.c.collection_id.in_(ids))
                    .order_by(source_readings.c.id)
                )
                for r in reading_rows:
                    readings[r.collection_id].append(_to_reading(r))
        return [
            PriceCollection(
                collected_at=_utc(row.collected_at),
                readings=tuple(readings[row.id]),
                median_cents=row.median_cents,
                published_cents=row.published_cents,
                published_quoted_at=(
                    _utc(row.published_quoted_at) if row.published_quoted_at else None
                ),
                outcome=CollectionOutcome(row.outcome),
                detail=row.detail,
            )
            for row in rows
        ]

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
    def add_local_observation(self, observation: LocalPriceObservation) -> LocalPriceObservation:
        with self._sessions() as session, session.begin():
            new_id = session.execute(
                insert(local_price_observations)
                .values(
                    observed_at=observation.observed_at.astimezone(UTC),
                    cooperative=observation.cooperative,
                    coffee_type=observation.coffee_type.value,
                    paid_soles=observation.paid_soles,
                    exchange_soles=observation.exchange_soles,
                )
                .returning(local_price_observations.c.id)
            ).scalar_one()
        return replace(observation, id=new_id)

    def local_observations_since(self, moment: datetime) -> list[LocalPriceObservation]:
        table = local_price_observations
        query = (
            select(table)
            .where(table.c.observed_at >= moment.astimezone(UTC))
            .order_by(table.c.observed_at.desc())
        )
        with self._sessions() as session:
            return [_observation(row) for row in session.execute(query)]

    def get_local_observation(self, observation_id: int) -> LocalPriceObservation | None:
        table = local_price_observations
        with self._sessions() as session:
            row = session.execute(select(table).where(table.c.id == observation_id)).first()
        return _observation(row) if row else None

    def update_local_paid(self, observation_id: int, paid_soles: Decimal) -> None:
        table = local_price_observations
        with self._sessions() as session, session.begin():
            session.execute(
                update(table).where(table.c.id == observation_id).values(paid_soles=paid_soles)
            )

    def delete_local_observation(self, observation_id: int) -> None:
        table = local_price_observations
        with self._sessions() as session, session.begin():
            session.execute(delete(table).where(table.c.id == observation_id))

    def add_local_observations(self, observations: Sequence[LocalPriceObservation]) -> None:
        if not observations:
            return
        with self._sessions() as session, session.begin():
            session.execute(
                insert(local_price_observations),
                [
                    {
                        "observed_at": o.observed_at.astimezone(UTC),
                        "cooperative": o.cooperative,
                        "coffee_type": o.coffee_type.value,
                        "paid_soles": o.paid_soles,
                        "exchange_soles": o.exchange_soles,
                    }
                    for o in observations
                ],
            )

    def count_local_observations_of(self, cooperatives: Sequence[str]) -> int:
        table = local_price_observations
        if not cooperatives:
            return 0
        query = select(func.count()).where(table.c.cooperative.in_(list(cooperatives)))
        with self._sessions() as session:
            return int(session.execute(query).scalar_one())

    def delete_local_observations_of(self, cooperatives: Sequence[str]) -> int:
        table = local_price_observations
        if not cooperatives:
            return 0
        names = list(cooperatives)
        with self._sessions() as session, session.begin():
            removed = session.execute(
                select(func.count()).where(table.c.cooperative.in_(names))
            ).scalar_one()
            session.execute(delete(table).where(table.c.cooperative.in_(names)))
        return int(removed)

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

    # ---------------------------------------------------------------- dólar en vivo (USD/PEN)
    def add_live_exchange_rate(self, rate: ExchangeRate) -> None:
        if rate.rated_at is None:
            raise ValueError("El dólar en vivo necesita la hora de la consulta")
        with self._sessions() as session, session.begin():
            session.execute(
                insert(live_exchange_rates).values(
                    rated_at=rate.rated_at.astimezone(UTC),
                    soles_per_dollar=rate.soles_per_dollar,
                    source=rate.source,
                )
            )

    def last_live_exchange_rate(self) -> ExchangeRate | None:
        query = select(live_exchange_rates).order_by(live_exchange_rates.c.rated_at.desc()).limit(1)
        with self._sessions() as session:
            row = session.execute(query).first()
        return _to_live_rate(row) if row else None

    def live_exchange_rates_between(self, start: datetime, end: datetime) -> list[ExchangeRate]:
        query = (
            select(live_exchange_rates)
            .where(live_exchange_rates.c.rated_at >= start.astimezone(UTC))
            .where(live_exchange_rates.c.rated_at < end.astimezone(UTC))
            .order_by(live_exchange_rates.c.rated_at)
        )
        with self._sessions() as session:
            return [_to_live_rate(row) for row in session.execute(query)]


def _to_live_rate(row: Row) -> ExchangeRate:  # type: ignore[type-arg]
    rated_at = _utc(row.rated_at)
    return ExchangeRate(
        Decimal(row.soles_per_dollar), rated_at.date(), row.source, rated_at=rated_at
    )


def _to_utc(moment: datetime | None) -> datetime | None:
    return moment.astimezone(UTC) if moment else None


def _to_reading(row: Row) -> SourceReading:  # type: ignore[type-arg]
    return SourceReading(
        source=row.source,
        status=ReadingStatus(row.status),
        cents_per_pound=row.cents_per_pound,
        quoted_at=_utc(row.quoted_at) if row.quoted_at else None,
        deviation_pct=row.deviation_pct,
        detail=row.detail,
        has_exchange_time=row.has_exchange_time,
    )


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


def _observation(row: Row) -> LocalPriceObservation:  # type: ignore[type-arg]
    return LocalPriceObservation(
        _utc(row.observed_at),
        row.cooperative,
        CoffeeType(row.coffee_type),
        Decimal(row.paid_soles),
        Decimal(row.exchange_soles),
        row.id,
    )
