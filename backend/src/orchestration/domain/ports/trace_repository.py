from typing import Protocol

from orchestration.domain.trace import AgentTrace


class TraceRepository(Protocol):
    def add(self, trace: AgentTrace) -> None: ...
