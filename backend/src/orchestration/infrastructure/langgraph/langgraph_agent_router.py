"""Adaptador del supervisor con LangGraph: un grafo con un nodo por agente."""

import logging
from collections.abc import Hashable, Iterable
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from shared.domain.agent_message import AgentMessage
from shared.domain.ports.agent import Agent
from shared.domain.ports.clock import Clock

logger = logging.getLogger(__name__)
_UNKNOWN = "unknown_receiver"


class _RoutingState(TypedDict):
    request: AgentMessage
    reply: AgentMessage | None


class LangGraphAgentRouter:
    """Implementa AgentRouter: START → (según el receptor) → nodo del agente → END."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._agents: dict[str, Agent] = {}
        self._graph = self._build_graph()

    def register(self, agents: Iterable[Agent]) -> None:
        """Registra los agentes y vuelve a construir el grafo.

        Se hace después de crear el supervisor porque el Agente Asesor necesita al
        supervisor para pedir datos a los demás agentes.
        """
        self._agents = {str(agent.name): agent for agent in agents}
        self._graph = self._build_graph()

    @property
    def agent_names(self) -> list[str]:
        return list(self._agents)

    def route(self, message: AgentMessage) -> AgentMessage:
        state = self._graph.invoke({"request": message, "reply": None})
        reply: AgentMessage | None = state["reply"]
        if reply is None:  # pragma: no cover - el grafo siempre produce respuesta
            return message.reply_failure("El supervisor no obtuvo respuesta", self._clock.now())
        return reply

    def _build_graph(self) -> Any:  # devuelve el grafo compilado de LangGraph
        graph = StateGraph(_RoutingState)
        for name, agent in self._agents.items():
            graph.add_node(name, _AgentNode(agent, self._clock))
            graph.add_edge(name, END)
        graph.add_node(_UNKNOWN, self._unknown_receiver_node)
        graph.add_edge(_UNKNOWN, END)
        destinations: dict[Hashable, str] = {name: name for name in [*self._agents, _UNKNOWN]}
        graph.add_conditional_edges(START, self._choose_agent, destinations)
        return graph.compile()

    def _choose_agent(self, state: _RoutingState) -> str:
        receiver = state["request"].receiver
        return receiver if receiver in self._agents else _UNKNOWN

    def _unknown_receiver_node(self, state: _RoutingState) -> dict[str, AgentMessage]:
        request = state["request"]
        return {
            "reply": request.reply_failure(
                f"Agente desconocido: {request.receiver}", self._clock.now()
            )
        }


class _AgentNode:
    """Nodo del grafo: entrega la solicitud a un agente y protege al sistema de sus errores."""

    def __init__(self, agent: Agent, clock: Clock) -> None:
        self._agent = agent
        self._clock = clock

    def __call__(self, state: _RoutingState) -> dict[str, AgentMessage]:
        request = state["request"]
        try:
            return {"reply": self._agent.handle(request)}
        except Exception:
            # Un error inesperado de un agente no debe tumbar al sistema
            logger.exception(
                "El agente %s falló con la acción %s", self._agent.name, request.action
            )
            return {"reply": request.reply_failure("Error interno del agente", self._clock.now())}
