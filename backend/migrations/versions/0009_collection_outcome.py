"""Resultado de cada consulta (publicada, sin cambios, no publicada o sin datos) y su motivo.

Solo agrega columnas (también si cada web informa la hora de la bolsa); las consultas
anteriores quedan como «publicada» o «no publicada».

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"


def upgrade() -> None:
    with op.batch_alter_table("price_collections") as batch:
        batch.add_column(
            sa.Column("outcome", sa.String(20), nullable=False, server_default="publicada")
        )
        batch.add_column(sa.Column("detail", sa.String(200), nullable=True))
    op.execute(
        "UPDATE price_collections SET outcome = 'no publicada' WHERE published_cents IS NULL"
    )
    with op.batch_alter_table("source_readings") as batch:
        batch.add_column(
            sa.Column("has_exchange_time", sa.Boolean, nullable=False, server_default=sa.true())
        )


def downgrade() -> None:
    with op.batch_alter_table("source_readings") as batch:
        batch.drop_column("has_exchange_time")
    with op.batch_alter_table("price_collections") as batch:
        batch.drop_column("detail")
        batch.drop_column("outcome")
