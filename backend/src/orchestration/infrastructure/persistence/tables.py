from sqlalchemy import Column, DateTime, Integer, String, Table

from shared.infrastructure.database import metadata

agent_traces = Table(
    "agent_traces",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conversation_id", String(36), nullable=False, index=True),
    Column("sender", String(20), nullable=False),
    Column("receiver", String(20), nullable=False),
    Column("action", String(40), nullable=False),
    Column("result", String(10), nullable=False),
    Column("duration_ms", Integer, nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    Column("detail", String(300), nullable=True),
)
