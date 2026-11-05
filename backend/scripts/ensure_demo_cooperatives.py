"""Carga los precios SINTÉTICOS de cooperativas al arrancar si DEMO_COOPERATIVES=true.

Solo si todavía no hay ninguno (no los regenera en cada reinicio). La bolsa y el tipo de cambio
que los acompañan son reales. El equipo puede borrarlos en «Equipo → Cooperativas».
"""

from market.application.manage_synthetic_data import ManageSyntheticData
from market.domain.quintal_price import PriceConverter
from market.infrastructure.persistence.sqlalchemy_cooperative_repository import (
    SqlAlchemyCooperativeRepository,
)
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import get_settings
from shared.infrastructure.system_clock import SystemClock


def main() -> None:
    settings = get_settings()
    if not settings.demo_cooperatives:
        print("DEMO_COOPERATIVES no está activo: no se cargan precios sintéticos.")
        return
    sessions = create_session_factory(create_db_engine(settings.database_url))
    manager = ManageSyntheticData(
        SqlAlchemyPriceRepository(sessions),
        SqlAlchemyCooperativeRepository(sessions),
        PriceConverter(settings.local_price_factor),
        SystemClock(),
    )
    if not manager.ensure_loaded():
        print(
            "Aviso: aún no hay precio real de la bolsa; la app reintentará cargar los precios "
            "sintéticos cada 5 minutos."
        )
        return
    status = manager.status()
    print(
        f"Precios sintéticos de demostración: {status.cooperatives} cooperativas "
        f"«JAENPERU sintético» con {status.observations} precios (bolsa real)."
    )


if __name__ == "__main__":
    main()
