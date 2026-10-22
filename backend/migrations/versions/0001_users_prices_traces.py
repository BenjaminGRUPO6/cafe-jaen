"""Iteración 1: usuarios, códigos de invitación, precios (en vivo y cierres) y trazas.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("phone", sa.String(9), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(100), nullable=False),
        sa.Column("consent_version", sa.String(20), nullable=False),
        sa.Column("consent_accepted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "invitation_codes",
        sa.Column("code", sa.String(12), primary_key=True),
        sa.Column("used_by", sa.String(36), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "live_quotes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("quoted_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("cents_per_pound", sa.Numeric(10, 4), nullable=False),
        sa.Column("sources", sa.String(120), nullable=False),
    )
    op.create_table(
        "quotations",
        sa.Column("quoted_on", sa.Date, primary_key=True),
        sa.Column("cents_per_pound", sa.Numeric(10, 4), nullable=False),
        sa.Column("source", sa.String(120), nullable=False),
    )
    op.create_table(
        "exchange_rates",
        sa.Column("rated_on", sa.Date, primary_key=True),
        sa.Column("soles_per_dollar", sa.Numeric(8, 4), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
    )
    op.create_table(
        "agent_traces",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.String(36), nullable=False, index=True),
        sa.Column("sender", sa.String(20), nullable=False),
        sa.Column("receiver", sa.String(20), nullable=False),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detail", sa.String(300), nullable=True),
    )


def downgrade() -> None:
    for table in (
        "agent_traces",
        "exchange_rates",
        "quotations",
        "live_quotes",
        "invitation_codes",
        "users",
    ):
        op.drop_table(table)
