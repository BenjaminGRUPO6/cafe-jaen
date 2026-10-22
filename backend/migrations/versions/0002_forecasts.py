"""Iteración 2: pronósticos del Agente Predictor.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    op.create_table(
        "forecasts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("generated_on", sa.Date, nullable=False, index=True),
        sa.Column("model_name", sa.String(30), nullable=False),
        sa.Column("mape", sa.Numeric(6, 2), nullable=False),
        sa.Column("points", sa.JSON, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("forecasts")
