from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Table

from shared.infrastructure.database import metadata

# Cotizaciones en vivo: una fila por cada precio consolidado (cada minuto con la bolsa abierta)
live_quotes = Table(
    "live_quotes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("quoted_at", DateTime(timezone=True), nullable=False, index=True),
    Column("cents_per_pound", Numeric(10, 4), nullable=False),
    Column("sources", String(120), nullable=False),
)

# Cierres diarios: el último precio de cada día (histórico de 30/90 días y pronóstico)
quotations = Table(
    "quotations",
    metadata,
    Column("quoted_on", Date, primary_key=True),
    Column("cents_per_pound", Numeric(10, 4), nullable=False),
    Column("source", String(120), nullable=False),
)

# Precios que pagan las cooperativas, anotados por el equipo junto a la bolsa del momento (HU12)
local_price_observations = Table(
    "local_price_observations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("observed_at", DateTime(timezone=True), nullable=False, index=True),
    Column("cooperative", String(80), nullable=False),
    Column("coffee_type", String(20), nullable=False),
    Column("paid_soles", Numeric(10, 2), nullable=False),
    Column("exchange_soles", Numeric(10, 2), nullable=False),
)

exchange_rates = Table(
    "exchange_rates",
    metadata,
    Column("rated_on", Date, primary_key=True),
    Column("soles_per_dollar", Numeric(8, 4), nullable=False),
    Column("source", String(50), nullable=False),
)
