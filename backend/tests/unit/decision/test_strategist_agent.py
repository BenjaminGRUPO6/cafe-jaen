"""HU05: el Estratega pide precio y pronóstico a otros agentes, siempre vía supervisor."""

from datetime import date

from decision.application.agents.strategist_agent import StrategistAgent
from decision.application.get_selling_advice import GetSellingAdvice
from decision.domain.selling_decision import SellingDecision
from shared.domain.agent_message import AgentMessage
from tests.fakes import FakeGateway, FixedClock
from tests.unit.advisor.test_grounding_and_templates import LIVE

CLOCK = FixedClock()
FORECAST = {
    "generated_on": "2026-11-03",
    "points": [
        {
            "date": "2026-11-05",
            "expected_soles": 1160.0,
            "lower_soles": 1145.0,
            "upper_soles": 1175.0,
        },
        {
            "date": "2026-11-06",
            "expected_soles": 1190.0,
            "lower_soles": 1150.0,
            "upper_soles": 1230.0,
        },
    ],
}


def agent(gateway: FakeGateway) -> StrategistAgent:
    return StrategistAgent(GetSellingAdvice(gateway, SellingDecision(), CLOCK), CLOCK, 61.5)


def ask(strategist: StrategistAgent, action: str = "get_selling_advice") -> AgentMessage:
    return strategist.handle(AgentMessage.request("api", "strategist", action, {}, CLOCK.now()))


def test_recommends_waiting_with_data_from_other_agents() -> None:
    gateway = FakeGateway(CLOCK)
    gateway.answer("analyst", "get_live_price", LIVE)
    gateway.answer("forecaster", "get_forecast", FORECAST)

    reply = ask(agent(gateway))

    assert reply.content["verdict"] == "Esperar"
    assert reply.content["target_date"] == "2026-11-06"
    assert reply.content["hit_rate_pct"] == 61.5
    assert "decisión de vender siempre es tuya" in reply.content["disclaimer"]
    assert [(m.sender, m.receiver) for m in gateway.requests] == [
        ("strategist", "analyst"),
        ("strategist", "forecaster"),
    ]


def test_without_price_does_not_recommend() -> None:
    gateway = FakeGateway(CLOCK)
    gateway.fail("analyst", "get_live_price")

    assert ask(agent(gateway)).content["verdict"] == "Sin datos suficientes"


def test_without_forecast_does_not_recommend() -> None:
    gateway = FakeGateway(CLOCK)
    gateway.answer("analyst", "get_live_price", LIVE)
    gateway.fail("forecaster", "get_forecast")

    assert ask(agent(gateway)).content["verdict"] == "Sin datos suficientes"
    assert CLOCK.today() == date(2026, 11, 4)


def test_unknown_action_returns_failure() -> None:
    assert ask(agent(FakeGateway(CLOCK)), "bailar").is_failure
