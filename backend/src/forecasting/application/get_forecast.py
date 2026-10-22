from forecasting.domain.errors import ForecastNotAvailableError
from forecasting.domain.forecast import Forecast
from forecasting.domain.ports.forecast_repository import ForecastRepository


class GetForecast:
    """HU06: devuelve el último pronóstico generado."""

    def __init__(self, repository: ForecastRepository) -> None:
        self._repository = repository

    def execute(self) -> Forecast:
        forecast = self._repository.latest()
        if forecast is None:
            raise ForecastNotAvailableError()
        return forecast
