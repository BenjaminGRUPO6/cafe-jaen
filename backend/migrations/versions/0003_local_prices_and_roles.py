"""Iteración 3 (HU12): precios de cooperativas y rol de administrador del equipo.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    op.create_table(
        "local_price_observations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("cooperative", sa.String(80), nullable=False),
        sa.Column("coffee_type", sa.String(20), nullable=False),
        sa.Column("paid_soles", sa.Numeric(10, 2), nullable=False),
        sa.Column("exchange_soles", sa.Numeric(10, 2), nullable=False),
    )
    # Los usuarios existentes son caficultores; los administradores se crean por script
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("role", sa.String(10), nullable=False, server_default="farmer"))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("role")
    op.drop_table("local_price_observations")
