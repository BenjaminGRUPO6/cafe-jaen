from datetime import date
from decimal import Decimal

from sqlalchemy import insert, select
from sqlalchemy.orm import Session, sessionmaker

from forecasting.domain.forecast import Forecast, ForecastPoint
from forecasting.infrastructure.persistence.tables import forecasts


class SqlAlchemyForecastRepository:
    """Implementa ForecastRepository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def save(self, forecast: Forecast) -> None:
        points = [
            {
                "day": p.day.isoformat(),
                "expected": str(p.expected),
                "lower": str(p.lower),
                "upper": str(p.upper),
            }
            for p in forecast.points
        ]
        with self._sessions() as session, session.begin():
            session.execute(
                insert(forecasts).values(
                    generated_on=forecast.generated_on,
                    model_name=forecast.model_name,
                    mape=forecast.mape,
                    points=points,
                )
            )

    def latest(self) -> Forecast | None:
        query = select(forecasts).order_by(forecasts.c.id.desc()).limit(1)
        with self._sessions() as session:
            row = session.execute(query).first()
        if row is None:
            return None
        points = tuple(
            ForecastPoint(
                date.fromisoformat(p["day"]),
                Decimal(p["expected"]),
                Decimal(p["lower"]),
                Decimal(p["upper"]),
            )
            for p in row.points
        )
        return Forecast(row.generated_on, row.model_name, Decimal(row.mape), points)
