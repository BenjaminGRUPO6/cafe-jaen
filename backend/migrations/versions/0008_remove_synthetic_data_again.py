"""Repite la limpieza de la 0007: quita precios «DEMO» guardados después de ella.

Si la versión nueva no llega a arrancar (por ejemplo, porque `QUOTATION_SOURCES` aún decía
«demo»), Render deja en línea la anterior, que siguió guardando precios sintéticos. Esta
migración los quita otra vez. Solo borra filas con fuente «DEMO …» y pronósticos (se generan de
nuevo al arrancar); no toca usuarios, cooperativas, precios anotados ni datos reales. Los
precios sintéticos de demostración de la v1.7 («Cooperativa JAENPERU sintético …») no se tocan:
el equipo los maneja desde «Equipo → Cooperativas».

Revision ID: 0008
Revises: 0007
"""

from alembic import op

revision = "0008"
down_revision = "0007"

DEMO = "'DEMO%'"


def upgrade() -> None:
    op.execute(
        "DELETE FROM source_readings WHERE collection_id IN ("
        f"SELECT collection_id FROM source_readings WHERE source LIKE {DEMO})"
    )
    op.execute(
        "DELETE FROM price_collections WHERE id NOT IN "
        "(SELECT DISTINCT collection_id FROM source_readings)"
    )
    op.execute(f"DELETE FROM live_quotes WHERE sources LIKE {DEMO}")
    op.execute(f"DELETE FROM quotations WHERE source LIKE {DEMO}")
    op.execute(f"DELETE FROM exchange_rates WHERE source LIKE {DEMO}")
    op.execute("DELETE FROM local_price_observations WHERE cooperative LIKE 'Cooperativa Demo %'")
    op.execute("DELETE FROM cooperatives WHERE name LIKE 'Cooperativa Demo %'")
    op.execute("DELETE FROM forecasts")


def downgrade() -> None:
    pass
