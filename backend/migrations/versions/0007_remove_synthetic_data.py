"""Quita todos los datos SINTÉTICOS de la demostración: la app trabaja solo con datos reales.

Borra solo lo que la demostración generó (fuentes «DEMO …», «Cooperativa Demo N» y los
pronósticos calculados sobre ese histórico) y los códigos DEMO que nadie usó. No toca usuarios,
cooperativas reales, precios anotados por el equipo ni datos de Yahoo Finance, Stooq o BCRP.
Al arrancar, scripts/start_server.sh carga el histórico real y genera un pronóstico nuevo.

Revision ID: 0007
Revises: 0006
"""

from alembic import op

revision = "0007"
down_revision = "0006"

DEMO = "'DEMO%'"
DEMO_COOPERATIVES = "'Cooperativa Demo %'"


def upgrade() -> None:
    # Las lecturas van primero: SQLite no aplica el borrado en cascada
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
    op.execute(f"DELETE FROM local_price_observations WHERE cooperative LIKE {DEMO_COOPERATIVES}")
    op.execute(f"DELETE FROM cooperatives WHERE name LIKE {DEMO_COOPERATIVES}")
    # Los pronósticos se calcularon sobre el histórico sintético: se vuelven a generar
    op.execute("DELETE FROM forecasts")
    # Códigos DEMO sin usar; los usados quedan porque identifican a un participante registrado
    op.execute("DELETE FROM invitation_codes WHERE code LIKE 'DEMO-%' AND used_by IS NULL")


def downgrade() -> None:
    # Los datos sintéticos no se recuperan (se volverían a generar con el script anterior)
    pass
