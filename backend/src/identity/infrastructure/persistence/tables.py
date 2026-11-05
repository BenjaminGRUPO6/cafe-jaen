from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, false

from shared.infrastructure.database import metadata

users = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("phone", String(9), nullable=False, unique=True),
    Column("password_hash", String(100), nullable=False),
    Column("consent_version", String(20), nullable=False),
    Column("consent_accepted_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("role", String(10), nullable=False, server_default="farmer"),
    Column("last_login_at", DateTime(timezone=True), nullable=True),
    Column("email", String(120), nullable=True, unique=True),
    Column("verified_at", DateTime(timezone=True), nullable=True),
)

invitation_codes = Table(
    "invitation_codes",
    metadata,
    Column("code", String(20), primary_key=True),
    Column("used_by", String(36), nullable=True),
    Column("used_at", DateTime(timezone=True), nullable=True),
    Column("role", String(10), nullable=False, server_default="farmer"),
)

# Código de 6 dígitos pendiente de cada cuenta sin verificar (se borra al verificar)
verification_codes = Table(
    "verification_codes",
    metadata,
    Column("user_id", String(36), primary_key=True),
    Column("code", String(6), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("attempts", Integer, nullable=False, server_default="0"),
    Column("email_sent", Boolean, nullable=False, server_default=false()),
)
