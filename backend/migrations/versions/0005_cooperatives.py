"""Catálogo de cooperativas de Jaén (HU12): agregar, editar y archivar desde «Equipo».

Carga cooperativas cafetaleras con sede en Jaén (fuentes públicas: Junta Nacional del Café,
Agraria.pe, registros de certificación orgánica OCIA) y registra en el catálogo los nombres que
ya tenían precios anotados, para no perder ningún dato.

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"

JAEN_COOPERATIVES = [
    ("CENFROCAFE – Central Fronteriza del Norte de Cafetaleros", None),
    ("Cooperativa de Servicios Múltiples Sol & Café", "https://www.solcafe.com.pe"),
    ("Cooperativa de Servicios Múltiples Jesús Solidario", None),
    ("Cooperativa Agraria Cafetalera Perú Andino", None),
    ("Cooperativa Agraria Café del Norte", None),
]


def upgrade() -> None:
    table = op.create_table(
        "cooperatives",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("location", sa.String(80), nullable=False, server_default="Jaén"),
        sa.Column("website", sa.String(200), nullable=True),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
    )
    connection = op.get_bind()
    known = {
        row[0]
        for row in connection.execute(
            sa.text("SELECT DISTINCT cooperative FROM local_price_observations")
        )
    }
    rows = [{"name": name, "location": "Jaén", "website": web} for name, web in JAEN_COOPERATIVES]
    official = {name.lower() for name, _ in JAEN_COOPERATIVES}
    rows += [
        {"name": name, "location": "Jaén", "website": None}
        for name in sorted(known)
        if name.lower() not in official
    ]
    op.bulk_insert(table, rows)


def downgrade() -> None:
    op.drop_table("cooperatives")
