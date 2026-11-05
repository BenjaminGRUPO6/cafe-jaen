"""Verificación por correo, códigos de invitación del equipo y eliminación de cuentas.

Las cuentas que ya existían quedan verificadas (se crearon antes de este requisito).

Revision ID: 0011
Revises: 0010
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("email", sa.String(120), nullable=True))
        batch.add_column(sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_unique_constraint("uq_users_email", ["email"])
    op.execute("UPDATE users SET verified_at = created_at WHERE verified_at IS NULL")
    with op.batch_alter_table("invitation_codes") as batch:
        batch.alter_column("code", type_=sa.String(20), existing_type=sa.String(12))
        batch.add_column(sa.Column("role", sa.String(10), nullable=False, server_default="farmer"))
    op.create_table(
        "verification_codes",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("email_sent", sa.Boolean, nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("verification_codes")
    with op.batch_alter_table("invitation_codes") as batch:
        batch.drop_column("role")
        batch.alter_column("code", type_=sa.String(12), existing_type=sa.String(20))
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("uq_users_email", type_="unique")
        batch.drop_column("verified_at")
        batch.drop_column("email")
