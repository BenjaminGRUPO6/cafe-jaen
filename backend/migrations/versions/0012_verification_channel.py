"""El código de verificación sale primero por WhatsApp: se guarda por qué canal se entregó.

Revision ID: 0012
Revises: 0011
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"


def upgrade() -> None:
    with op.batch_alter_table("verification_codes") as batch:
        batch.add_column(sa.Column("delivered_by", sa.String(10), nullable=True))
    op.execute("UPDATE verification_codes SET delivered_by = 'email' WHERE email_sent")
    with op.batch_alter_table("verification_codes") as batch:
        batch.drop_column("email_sent")


def downgrade() -> None:
    with op.batch_alter_table("verification_codes") as batch:
        batch.add_column(
            sa.Column("email_sent", sa.Boolean, nullable=False, server_default=sa.false())
        )
    op.execute("UPDATE verification_codes SET email_sent = delivered_by IS NOT NULL")
    with op.batch_alter_table("verification_codes") as batch:
        batch.drop_column("delivered_by")
