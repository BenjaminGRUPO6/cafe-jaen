"""Modelo de lenguaje por palabras clave: funciona sin internet ni costo.

Se usa en desarrollo, en las pruebas y como respaldo si el LLM no está disponible.
"""

from typing import Any

from advisor.domain.templates import template_answer
from advisor.domain.text import normalize
from advisor.domain.tools import TOOLS, ToolCall
from shared.domain.contract import Action

_RULES: list[tuple[Action, tuple[str, ...]]] = [
    (
        Action.GET_SELLING_ADVICE,
        ("vendo", "vender", "espero", "esperar", "conviene", "guardo", "guardar", "recomiend"),
    ),
    (
        Action.GET_FORECAST,
        (
            "pronostic",
            "subira",
            "bajara",
            "va a estar",
            "proxima semana",
            "manana",
            "predic",
            "futuro",
        ),
    ),
    (
        Action.GET_PRICE_HISTORY,
        ("historic", "ultimos", "mes pasado", "tendencia", "dias atras", "grafic"),
    ),
    (
        Action.GET_LOCAL_PRICES,
        (
            "cooperativa",
            "cenfrocafe",
            "sol & cafe",
            "sol y cafe",
            "jesus solidario",
            "peru andino",
            "cafe del norte",
            "acopio",
            "pagan en jaen",
            "paga en jaen",
            "cuanto paga",
            "cuanto pagan",
        ),
    ),
    (
        Action.GET_LIVE_PRICE,
        ("precio", "cuanto", "quintal", "cotiza", "hoy", "vale", "esta el cafe", "bolsa", "ahora"),
    ),
]


class KeywordLanguageModel:
    """Implementa LanguageModel con reglas simples y respuestas con plantilla."""

    def choose_tool(self, question: str) -> ToolCall | None:
        text = normalize(question)
        for action, keywords in _RULES:
            if any(keyword in text for keyword in keywords):
                return ToolCall(TOOLS[action], _arguments(action, text))
        return None

    def write_answer(self, question: str, action: str, data: dict[str, Any]) -> str:
        return template_answer(action, data)


def _arguments(action: Action, text: str) -> dict[str, Any]:
    if action is not Action.GET_PRICE_HISTORY:
        return {}
    if "90" in text:
        return {"period": "90"}
    return {"period": "today" if "hoy" in text else "30"}
