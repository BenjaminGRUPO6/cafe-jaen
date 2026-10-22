"""PA-08-1 y PA-08-3 (HU08) a nivel de caso de uso."""

from typing import Any

import pytest

from advisor.application.agents.advisor_agent import AdvisorAgent
from advisor.application.answer_question import AnswerQuestion
from advisor.domain.answer import NO_INFORMATION, SERVICE_UNAVAILABLE
from advisor.domain.tools import ToolCall
from advisor.infrastructure.llm.keyword_language_model import KeywordLanguageModel
from shared.domain.agent_message import AgentMessage
from tests.fakes import FakeGateway, FixedClock
from tests.unit.advisor.test_grounding_and_templates import LIVE


@pytest.fixture
def gateway() -> FakeGateway:
    gateway = FakeGateway()
    gateway.answer("analyst", "get_live_price", LIVE)
    return gateway


def test_answers_live_price_through_the_supervisor(gateway: FakeGateway) -> None:
    answer = AnswerQuestion(KeywordLanguageModel(), gateway).execute(
        "¿A cuánto está el quintal hoy?"
    )

    assert "S/ 1140,89" in answer.text
    assert answer.sources == ("Yahoo Finance", "Stooq", "BCRP")
    assert gateway.requests[0].sender == "advisor"  # pidió el dato como asesor, no por la BD


def test_off_topic_question_gets_no_information(gateway: FakeGateway) -> None:
    answer = AnswerQuestion(KeywordLanguageModel(), gateway).execute(
        "¿Quién ganó el partido de ayer?"
    )

    assert answer.text == NO_INFORMATION
    assert gateway.requests == []


def test_failure_of_the_data_agent_is_explained(gateway: FakeGateway) -> None:
    gateway.fail("analyst", "get_live_price")

    assert (
        AnswerQuestion(KeywordLanguageModel(), gateway).execute("precio de hoy").text
        == SERVICE_UNAVAILABLE
    )


class InventingLanguageModel(KeywordLanguageModel):
    """Simula un LLM que inventa un precio."""

    def write_answer(self, question: str, action: str, data: dict[str, Any]) -> str:
        return "Hoy el quintal está a S/ 1500,00."


def test_invented_numbers_are_replaced_by_template(gateway: FakeGateway) -> None:
    answer = AnswerQuestion(InventingLanguageModel(), gateway).execute("precio de hoy")

    assert "1500" not in answer.text and "1140,89" in answer.text


@pytest.mark.parametrize(
    ("question", "action", "arguments"),
    [
        ("¿cuánto está el café hoy?", "get_live_price", {}),
        ("¿va a subir la próxima semana?", "get_forecast", {}),
        ("muéstrame el histórico de 90 días", "get_price_history", {"period": "90"}),
        ("muéstrame el gráfico de hoy", "get_price_history", {"period": "today"}),
        ("¿vendo hoy o espero?", "get_selling_advice", {}),
    ],
)
def test_keyword_model_chooses_the_right_tool(
    question: str, action: str, arguments: dict[str, Any]
) -> None:
    tool = KeywordLanguageModel().choose_tool(question)

    assert isinstance(tool, ToolCall)
    assert (tool.spec.action, tool.arguments) == (action, arguments)


def test_advisor_agent_wraps_the_answer(gateway: FakeGateway) -> None:
    clock = FixedClock()
    agent = AdvisorAgent(AnswerQuestion(KeywordLanguageModel(), gateway), clock)

    reply = agent.handle(
        AgentMessage.request(
            "api", "advisor", "answer_question", {"question": "precio hoy"}, clock.now()
        )
    )

    assert reply.content["used_tool"] == "get_live_price"
    assert agent.handle(AgentMessage.request("api", "advisor", "otra", {}, clock.now())).is_failure
