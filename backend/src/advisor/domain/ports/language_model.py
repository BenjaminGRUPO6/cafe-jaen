from typing import Any, Protocol

from advisor.domain.tools import ToolCall


class LanguageModel(Protocol):
    """Puerto de salida: el modelo de lenguaje que interpreta y redacta."""

    def choose_tool(self, question: str) -> ToolCall | None:
        """Elige la herramienta que responde la pregunta, o None si está fuera de tema."""
        ...

    def write_answer(self, question: str, action: str, data: dict[str, Any]) -> str:
        """Redacta la respuesta usando solo `data`."""
        ...
