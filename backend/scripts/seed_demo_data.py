"""Datos SINTÉTICOS para desarrollo local sin internet (NO usar en el experimento).

Genera 2 años de cierres diarios, las cotizaciones minuto a minuto del último día hábil
y crea el código DEMO-0001. Para que el precio «se mueva» en vivo sin internet, arranca la
API con QUOTATION_SOURCES='["demo"]' (ver README).
Uso:  python scripts/seed_demo_data.py
"""

import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
)
from market.domain.market_hours import NEW_YORK
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings

SOURCE = "DEMO (sintético)"


def main() -> None:
    sessions = create_session_factory(create_db_engine(get_settings().database_url))
    prices = SqlAlchemyPriceRepository(sessions)
    rng = random.Random(7)
    cents, rate = 250.0, 3.75
    day = date.today() - timedelta(days=730)
    last_business_day = day
    while day <= date.today():
        if day.weekday() < 5:  # solo días hábiles
            cents = max(100.0, cents * (1 + rng.gauss(0.0003, 0.015)))
            rate = rate + rng.gauss(0, 0.004)
            prices.save_daily_close(Quotation(Decimal(f"{cents:.2f}"), day, SOURCE))
            prices.add_exchange_rate(ExchangeRate(Decimal(f"{rate:.3f}"), day, SOURCE))
            last_business_day = day
        day += timedelta(days=1)

    # Minuto a minuto (cada 5 min) del último día hábil, para el gráfico «Hoy»
    moment = datetime.combine(last_business_day, time(4, 15), tzinfo=NEW_YORK)
    close = datetime.combine(last_business_day, time(13, 30), tzinfo=NEW_YORK)
    intraday = cents * 0.99
    while moment <= min(close, datetime.now(NEW_YORK)):
        intraday *= 1 + rng.gauss(0.0001, 0.001)
        prices.add_live_quote(LiveQuote(Decimal(f"{intraday:.2f}"), moment, (SOURCE,)))
        moment += timedelta(minutes=5)

    SqlAlchemyInvitationCodeRepository(sessions).add_many(["DEMO-0001"])
    print("Datos de demostración cargados. Código de invitación: DEMO-0001")


if __name__ == "__main__":
    main()
