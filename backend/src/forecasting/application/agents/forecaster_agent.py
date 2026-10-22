from typing import Any

from forecasting.application.generate_forecast import GenerateForecast
from forecasting.application.get_forecast import GetForecast
from forecasting.domain.errors import ForecastingError
from forecasting.domain.forecast import DISCLAIMER, Forecast
from shared.domain.agent_message import AgentMessage
from shared.domain.contract import Action, AgentName
from shared.domain.ports.clock import Clock


class ForecasterAgent:
    """Agente Predictor: genera cada día el pronóstico y lo entrega cuando se le pide."""

    name = AgentName.FORECASTER

    def __init__(self, generate: GenerateForecast, get: GetForecast, clock: Clock) -> None:
        self._generate = generate
        self._get = get
        self._clock = clock

    def handle(self, message: AgentMessage) -> AgentMessage:
        now = self._clock.now()
        try:
            if message.action == Action.GENERATE_FORECAST:
                # El historial llega del Analista, a través del supervisor
                history = [float(point["price_soles"]) for point in message.content["points"]]
                return message.reply_inform(_to_dict(self._generate.execute(history)), now)
            if message.action == Action.GET_FORECAST:
                return message.reply_inform(_to_dict(self._get.execute()), now)
        except ForecastingError as error:
            return message.reply_failure(str(error), now)
        return message.reply_failure(f"Acción no soportada: {message.action}", now)


def _to_dict(forecast: Forecast) -> dict[str, Any]:
    return {
        "generated_on": forecast.generated_on.isoformat(),
        "model": forecast.model_name,
        "mape": float(forecast.mape),
        "unit": "S/ por quintal (46 kg)",
        "disclaimer": DISCLAIMER,
        "points": [
            {
                "date": p.day.isoformat(),
                "expected_soles": float(p.expected),
                "lower_soles": float(p.lower),
                "upper_soles": float(p.upper),
            }
            for p in forecast.points
        ],
    }
