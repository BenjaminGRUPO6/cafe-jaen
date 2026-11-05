"""Carga el histórico REAL de cierres diarios y tipo de cambio (gráfico y Predictor).

Prueba Yahoo Finance y, si no responde, Stooq; el tipo de cambio sale del BCRP.
Es idempotente: si ya hay histórico suficiente, no hace nada (usa --force para completar).

Uso:  python scripts/load_price_history.py --years 5
"""

import argparse

from market.application.load_price_history import LoadPriceHistory
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from market.infrastructure.sources.bcrp_exchange_rate_provider import BcrpExchangeRateProvider
from market.infrastructure.sources.stooq_quotation_source import StooqQuotationSource
from market.infrastructure.sources.yahoo_quotation_source import YahooQuotationSource
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", type=int, default=5)
    parser.add_argument("--force", action="store_true", help="completa aunque ya haya histórico")
    args = parser.parse_args()
    settings = get_settings()
    repository = SqlAlchemyPriceRepository(
        create_session_factory(create_db_engine(settings.database_url))
    )
    loader = LoadPriceHistory(
        [YahooQuotationSource(), StooqQuotationSource(timezone=settings.stooq_timezone)],
        BcrpExchangeRateProvider(),
        repository,
        SystemClock(),
    )
    report = loader.execute(args.years, force=args.force)
    if report.skipped:
        print("Histórico real: ya estaba cargado.")
        return
    print(
        f"Histórico real: {report.closes_saved} cierres diarios ({report.source or 'ninguna web'})"
        f" · {report.rates_saved} tipos de cambio del BCRP"
    )
    for issue in report.issues:
        print(f"  Aviso: {issue}")


if __name__ == "__main__":
    main()
