"""PA-08-2 y PA-08-3 (HU08): batería de 20 preguntas.

Criterio: 0 precios inventados y cada respuesta con fuente, o «No tengo esa información»
cuando la pregunta está fuera de tema.
"""

import pytest

from advisor.application.answer_question import AnswerQuestion
from advisor.domain.answer import NO_INFORMATION
from advisor.domain.grounding import is_grounded
from advisor.infrastructure.llm.keyword_language_model import KeywordLanguageModel
from tests.fakes import FakeGateway
from tests.unit.advisor.test_grounding_and_templates import ADVICE, LIVE

HISTORY = {
    "period": "30",
    "points": [
        {"date": "2026-10-05", "price_soles": 1080.5},
        {"date": "2026-11-04", "price_soles": 1140.89},
    ],
}
FORECAST = {
    "disclaimer": "Pronóstico referencial: no es una recomendación de venta.",
    "points": [
        {
            "date": "2026-11-13",
            "expected_soles": 1152.3,
            "lower_soles": 1110.4,
            "upper_soles": 1194.2,
        }
    ],
}
DATA = {
    "get_live_price": LIVE,
    "get_price_history": HISTORY,
    "get_forecast": FORECAST,
    "get_selling_advice": ADVICE,
}

BATTERY = [
    ("¿A cuánto está el quintal hoy?", "get_live_price"),
    ("¿Cuál es el precio del café?", "get_live_price"),
    ("cuanto vale mi cafe", "get_live_price"),
    ("¿Cómo cotiza el café en la bolsa?", "get_live_price"),
    ("precio de ahora", "get_live_price"),
    ("¿El precio subirá la próxima semana?", "get_forecast"),
    ("¿Qué pronóstico hay?", "get_forecast"),
    ("¿Cómo va a estar el precio mañana?", "get_forecast"),
    ("¿Bajará el café?", "get_forecast"),
    ("Muéstrame el histórico", "get_price_history"),
    ("¿Cómo fue la tendencia del mes pasado?", "get_price_history"),
    ("precios de los últimos 90 días", "get_price_history"),
    ("¿Vendo hoy o espero?", "get_selling_advice"),
    ("¿Me conviene vender mi café ahora?", "get_selling_advice"),
    ("¿Guardo mi café unos días más?", "get_selling_advice"),
    ("¿Quién ganó el partido de ayer?", None),
    ("¿Cómo curo la roya?", None),
    ("Cuéntame un chiste", None),
    ("¿Qué clima hará en Jaén?", None),
    ("hola", None),
]


@pytest.fixture
def advisor() -> AnswerQuestion:
    gateway = FakeGateway()
    for receiver, action in [
        ("analyst", "get_live_price"),
        ("analyst", "get_price_history"),
        ("forecaster", "get_forecast"),
        ("strategist", "get_selling_advice"),
    ]:
        gateway.answer(receiver, action, DATA[action])
    return AnswerQuestion(KeywordLanguageModel(), gateway)


def test_battery_has_twenty_questions() -> None:
    assert len(BATTERY) == 20


@pytest.mark.parametrize(("question", "expected_tool"), BATTERY)
def test_answer_is_grounded_or_declines(
    advisor: AnswerQuestion, question: str, expected_tool: str | None
) -> None:
    answer = advisor.execute(question)

    assert answer.used_tool == expected_tool
    if expected_tool is None:
        assert answer.text == NO_INFORMATION
    else:
        assert is_grounded(answer.text, DATA[expected_tool]), answer.text
        assert answer.sources
