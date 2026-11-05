from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, false

from shared.infrastructure.database import metadata

# Conversaciones de «Atención»: una por caficultor (user_id), con preguntas y respuestas
support_messages = Table(
    "support_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String(36), nullable=False, index=True),
    Column("author", String(10), nullable=False),
    Column("text", String(1000), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("read", Boolean, nullable=False, server_default=false()),
)
