"""Carga el histórico de cierres diarios y tipo de cambio (insumo del gráfico y del Predictor).

Uso:  python scripts/load_price_history.py --years 5
"""

import argparse
from datetime import date, timedelta

from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from market.infrastructure.sources.bcrp_exchange_rate_provider import BcrpExchangeRateProvider
from market.infrastructure.sources.yahoo_quotation_source import YahooQuotationSource
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", type=int, default=5)
    start = date.today() - timedelta(days=365 * parser.parse_args().years)

    repository = SqlAlchemyPriceRepository(
        create_session_factory(create_db_engine(get_settings().database_url))
    )
    existing = {q.quoted_on for q in repository.quotations_since(start)}

    quotations = [
        q for q in YahooQuotationSource().fetch_daily_history(start) if q.quoted_on not in existing
    ]
    for quotation in quotations:
        repository.save_daily_close(quotation)

    # El BCRP limita el tamaño de cada consulta: se pide año por año
    rates = 0
    for year_start in range(start.year, date.today().year + 1):
        chunk_start = max(start, date(year_start, 1, 1))
        chunk_end = min(date.today(), date(year_start, 12, 31))
        for rate in BcrpExchangeRateProvider().fetch_history(chunk_start, chunk_end):
            repository.add_exchange_rate(rate)
            rates += 1
    print(f"Cierres diarios nuevos: {len(quotations)} · Tipos de cambio: {rates}")


if __name__ == "__main__":
    main()
