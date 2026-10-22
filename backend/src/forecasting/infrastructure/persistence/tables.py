from sqlalchemy import JSON, Column, Date, Integer, Numeric, String, Table

from shared.infrastructure.database import metadata

forecasts = Table(
    "forecasts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("generated_on", Date, nullable=False, index=True),
    Column("model_name", String(30), nullable=False),
    Column("mape", Numeric(6, 2), nullable=False),
    # Lista de {day, expected, lower, upper}; siempre se lee completa
    Column("points", JSON, nullable=False),
)
