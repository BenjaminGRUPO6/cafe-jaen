"""Contrato entre agentes: nombres de agentes y acciones.

Se acordó en la Iteración 0 y no se cambia sin acuerdo de ambos integrantes.
"""

from enum import StrEnum


class AgentName(StrEnum):
    """Nombre con el que cada agente se registra en el supervisor."""

    API = "api"
    SCHEDULER = "scheduler"
    SUPERVISOR = "supervisor"
    COLLECTOR = "collector"
    ANALYST = "analyst"
    FORECASTER = "forecaster"
    STRATEGIST = "strategist"
    ADVISOR = "advisor"


class Action(StrEnum):
    """Acciones que los agentes saben atender."""

    COLLECT_PRICES = "collect_prices"  # Recolector
    GET_LIVE_PRICE = "get_live_price"  # Analista
    GET_PRICE_HISTORY = "get_price_history"  # Analista
    RECORD_LOCAL_PRICE = "record_local_price"  # Analista (solo administrador)
    GET_LOCAL_PRICES = "get_local_prices"  # Analista (solo administrador)
    GENERATE_FORECAST = "generate_forecast"  # Predictor
    GET_FORECAST = "get_forecast"  # Predictor
    GET_SELLING_ADVICE = "get_selling_advice"  # Estratega de venta
    ANSWER_QUESTION = "answer_question"  # Asesor
