from sqlalchemy import Column, DateTime, String, Table

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
)

invitation_codes = Table(
    "invitation_codes",
    metadata,
    Column("code", String(12), primary_key=True),
    Column("used_by", String(36), nullable=True),
    Column("used_at", DateTime(timezone=True), nullable=True),
)
