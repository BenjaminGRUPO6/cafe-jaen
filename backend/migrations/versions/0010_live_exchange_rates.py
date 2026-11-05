"""Dólar en vivo (USD/PEN) de cada consulta del Recolector, además del oficial diario del BCRP.

Revision ID: 0010
Revises: 0009
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"


def upgrade() -> None:
    op.create_table(
        "live_exchange_rates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("rated_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("soles_per_dollar", sa.Numeric(8, 4), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("live_exchange_rates")
