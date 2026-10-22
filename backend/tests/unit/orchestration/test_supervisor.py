"""PA-07-1 a PA-07-4 (HU07): enrutamiento, fallos controlados y trazas."""

from datetime import date

import pytest

from orchestration.application.dispatch_request import DispatchRequest
from orchestration.application.run_daily_cycle import CollectLivePrices, RunDailyCycle
from orchestration.infrastructure.langgraph.langgraph_agent_router import LangGraphAgentRouter
from shared.domain.agent_message import AgentMessage, Performative
from tests.fakes import FakeGateway, FixedClock, InMemoryTraceRepository

CLOCK = FixedClock()


class EchoAgent:
    def __init__(self, name: str) -> None:
        self.name = name

    def handle(self, message: AgentMessage) -> AgentMessage:
        return message.reply_inform(
            {"handled_by": self.name, "action": message.action}, CLOCK.now()
        )


class BrokenAgent:
    name = "analyst"

    def handle(self, message: AgentMessage) -> AgentMessage:
        raise RuntimeError("error inesperado")


@pytest.fixture
def traces() -> InMemoryTraceRepository:
    return InMemoryTraceRepository()


def supervisor_with(agents: list[object], traces: InMemoryTraceRepository) -> DispatchRequest:
    router = LangGraphAgentRouter(CLOCK)
    router.register(agents)  # type: ignore[arg-type]
    return DispatchRequest(router, traces, CLOCK)


@pytest.mark.parametrize(
    "receiver", ["collector", "analyst", "forecaster", "strategist", "advisor"]
)
def test_routes_each_request_to_the_right_agent(
    receiver: str, traces: InMemoryTraceRepository
) -> None:
    names = ("collector", "analyst", "forecaster", "strategist", "advisor")
    agents = [EchoAgent(name) for name in names]

    reply = supervisor_with(agents, traces).request("api", receiver, "any_action")  # type: ignore[arg-type]

    assert reply.content["handled_by"] == receiver
    assert reply.receiver == "api"


def test_agent_exception_becomes_failure(traces: InMemoryTraceRepository) -> None:
    reply = supervisor_with([BrokenAgent()], traces).request("api", "analyst", "get_live_price")

    assert reply.performative is Performative.FAILURE


def test_unknown_receiver_becomes_failure(traces: InMemoryTraceRepository) -> None:
    reply = supervisor_with([EchoAgent("analyst")], traces).request("api", "nadie", "x")

    assert reply.is_failure and "desconocido" in reply.content["reason"]


def test_every_interaction_is_traced(traces: InMemoryTraceRepository) -> None:
    supervisor = supervisor_with([EchoAgent("analyst"), BrokenAgent()], traces)
    supervisor.request("api", "analyst", "get_live_price")

    trace = traces.traces[0]
    assert (trace.sender, trace.receiver, trace.action) == ("api", "analyst", "get_live_price")
    assert trace.duration_ms >= 0 and trace.recorded_at == CLOCK.now()


def test_daily_cycle_passes_history_from_analyst_to_forecaster() -> None:
    gateway = FakeGateway()
    points = [{"date": date(2026, 11, 4).isoformat(), "price_soles": 1140.89}]
    gateway.answer("collector", "collect_prices", {"quotation_saved": True})
    gateway.answer("analyst", "get_price_history", {"points": points})
    gateway.answer("forecaster", "generate_forecast", {"model": "elm"})

    report = RunDailyCycle(gateway, history_days=1825).execute()

    assert report.forecast_generated
    assert [m.receiver for m in gateway.requests] == ["collector", "analyst", "forecaster"]
    assert gateway.requests[0].content == {"force": True}  # guarda el cierre del día
    assert gateway.requests[1].content == {"period": "1825"}
    assert gateway.requests[2].content == {"points": points}


def test_daily_cycle_stops_if_history_is_not_available() -> None:
    gateway = FakeGateway()
    gateway.answer("collector", "collect_prices", {})
    gateway.fail("analyst", "get_price_history", "sin datos")

    report = RunDailyCycle(gateway, history_days=30).execute()

    assert not report.forecast_generated and report.detail == "sin datos"


def test_live_collection_asks_the_collector() -> None:
    gateway = FakeGateway()
    gateway.answer("collector", "collect_prices", {"quotation_saved": True})

    assert CollectLivePrices(gateway).execute() == {"quotation_saved": True}
    assert gateway.requests[0].sender == "scheduler"
