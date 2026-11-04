"""Datos SINTÉTICOS para desarrollo local sin internet (NO usar en el experimento).

Genera 2 años de cierres diarios, las cotizaciones minuto a minuto del último día hábil,
precios de cooperativas DE EJEMPLO para el «Precio estimado en Jaén» y el código DEMO-0001.
Para que el precio «se mueva» en vivo sin internet, `python dev.py start` arranca la API
con QUOTATION_SOURCES='["demo"]' (ver README).
Uso:  python dev.py demo
"""

import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
)
from market.domain.local_price import CoffeeType, LocalPriceObservation
from market.domain.market_hours import NEW_YORK
from market.domain.quintal_price import PriceConverter
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings

SOURCE = "DEMO (sintético)"

# Porcentaje de la bolsa que pagan las cooperativas de ejemplo, por tipo de café
DEMO_RATIOS = {
    CoffeeType.CONVENTIONAL: (0.71, 0.73, 0.72),
    CoffeeType.ORGANIC: (0.80, 0.82, 0.81),
    CoffeeType.SPECIALTY: (0.91, 0.94, 0.92),
}


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

    # Precios de cooperativas de ejemplo (nombres ficticios) anotados hoy
    settings = get_settings()
    exchange = PriceConverter(settings.local_price_factor).to_quintal(
        Decimal(f"{cents:.2f}"), Decimal(f"{rate:.3f}")
    )
    now = datetime.now(NEW_YORK)
    for coffee_type, ratios in DEMO_RATIOS.items():
        for number, ratio in enumerate(ratios, start=1):
            paid = (exchange.soles * Decimal(str(ratio))).quantize(Decimal("0.01"))
            prices.add_local_observation(
                LocalPriceObservation(
                    now - timedelta(days=number),
                    f"Cooperativa Demo {number}",
                    coffee_type,
                    paid,
                    exchange.soles,
                )
            )

    SqlAlchemyInvitationCodeRepository(sessions).add_many(["DEMO-0001"])
    print("Datos de demostración cargados. Código de invitación: DEMO-0001")


if __name__ == "__main__":
    main()
