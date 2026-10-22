from sqlalchemy import insert
from sqlalchemy.orm import Session, sessionmaker

from orchestration.domain.trace import AgentTrace
from orchestration.infrastructure.persistence.tables import agent_traces


class SqlAlchemyTraceRepository:
    """Implementa TraceRepository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._sessions = session_factory

    def add(self, trace: AgentTrace) -> None:
        with self._sessions() as session, session.begin():
            session.execute(
                insert(agent_traces).values(
                    conversation_id=str(trace.conversation_id),
                    sender=trace.sender,
                    receiver=trace.receiver,
                    action=trace.action,
                    result=trace.result.value,
                    duration_ms=trace.duration_ms,
                    recorded_at=trace.recorded_at,
                    detail=(trace.detail or "")[:300] or None,
                )
            )
