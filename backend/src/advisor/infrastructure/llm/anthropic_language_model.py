"""Adaptador del LLM real (API de Anthropic).

Solo se usa si LLM_PROVIDER=anthropic y hay ANTHROPIC_API_KEY. Si la respuesta
contiene números que no están en los datos, el caso de uso la reemplaza por la
plantilla (ver advisor/domain/grounding.py).
"""

import json
from typing import Any

import anthropic
from anthropic.types import ToolParam

from advisor.domain.tools import TOOLS, ToolCall
from shared.domain.contract import Action

_CHOOSE_SYSTEM = (
    "Eres el asesor de precios de café de una app para caficultores de Jaén (Perú). "
    "Elige la herramienta que responde la pregunta. Si la pregunta no trata del precio del café, "
    "su histórico, su pronóstico o si conviene vender o esperar, no uses ninguna herramienta."
)
_WRITE_SYSTEM = (
    "Responde en español sencillo, en máximo 3 oraciones, usando SOLO los datos JSON entregados. "
    "No inventes números. Escribe los montos como 'S/ 1140,89' "
    "(coma decimal, sin separador de miles). "
    "Menciona la hora o fecha y la fuente. No des tu propia recomendación de venta: si los datos "
    "traen una (campo verdict), explícala tal cual con su motivo y su aviso."
)


class AnthropicLanguageModel:
    """Implementa LanguageModel con la API de mensajes y herramientas de Anthropic."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 300) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def choose_tool(self, question: str) -> ToolCall | None:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=_CHOOSE_SYSTEM,
            tools=[_tool_schema(action) for action in TOOLS],
            messages=[{"role": "user", "content": question}],
        )
        for block in response.content:
            if block.type == "tool_use" and block.name in TOOLS:
                return ToolCall(TOOLS[Action(block.name)], dict(block.input))
        return None

    def write_answer(self, question: str, action: str, data: dict[str, Any]) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=_WRITE_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"Pregunta: {question}\nDatos ({action}): {_as_json(data)}",
                }
            ],
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()


def _tool_schema(action: Action) -> ToolParam:
    spec = TOOLS[action]
    properties = {
        name: {"type": "string", "description": text} for name, text in spec.parameters.items()
    }
    return {
        "name": spec.action.value,
        "description": spec.description,
        "input_schema": {"type": "object", "properties": properties, "required": list(properties)},
    }


def _as_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False)
