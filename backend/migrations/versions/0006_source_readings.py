"""Registro de cada consulta del Recolector con lo que marcó cada web (pestaña «Bolsa»).

Solo agrega tablas nuevas: no modifica ni borra datos existentes.

Revision ID: 0006
Revises: 0005
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"


def upgrade() -> None:
    op.create_table(
        "price_collections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("median_cents", sa.Numeric(10, 4), nullable=True),
        sa.Column("published_cents", sa.Numeric(10, 4), nullable=True),
        sa.Column("published_quoted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_price_collections_collected_at", "price_collections", ["collected_at"])
    op.create_table(
        "source_readings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "collection_id",
            sa.Integer,
            sa.ForeignKey("price_collections.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("cents_per_pound", sa.Numeric(10, 4), nullable=True),
        sa.Column("quoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deviation_pct", sa.Numeric(8, 2), nullable=True),
        sa.Column("detail", sa.String(200), nullable=True),
    )
    op.create_index("ix_source_readings_collection_id", "source_readings", ["collection_id"])


def downgrade() -> None:
    op.drop_table("source_readings")
    op.drop_table("price_collections")
