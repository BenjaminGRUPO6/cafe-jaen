"""Herramientas que el Agente Asesor puede usar: cada una es una acción de otro agente."""

from dataclasses import dataclass, field
from typing import Any

from shared.domain.contract import Action, AgentName


@dataclass(frozen=True)
class ToolSpec:
    action: Action
    receiver: AgentName
    description: str
    parameters: dict[str, str] = field(default_factory=dict)  # nombre -> descripción


@dataclass(frozen=True)
class ToolCall:
    """Herramienta elegida para responder una pregunta, con sus argumentos."""

    spec: ToolSpec
    arguments: dict[str, Any] = field(default_factory=dict)


TOOLS: dict[Action, ToolSpec] = {
    spec.action: spec
    for spec in (
        ToolSpec(
            Action.GET_LIVE_PRICE,
            AgentName.ANALYST,
            "Precio del café ahora en la bolsa de Nueva York, en ¢USD/lb y S/ por quintal",
        ),
        ToolSpec(
            Action.GET_PRICE_HISTORY,
            AgentName.ANALYST,
            "Precios de hoy (minuto a minuto) o de los últimos 30 o 90 días",
            {"period": "today, 30 o 90"},
        ),
        ToolSpec(
            Action.GET_FORECAST,
            AgentName.FORECASTER,
            "Pronóstico del precio para los próximos 7 días hábiles",
        ),
        ToolSpec(
            Action.GET_SELLING_ADVICE,
            AgentName.STRATEGIST,
            "Recomendación: vender ahora, esperar o sin señal clara, con su motivo",
        ),
    )
}
