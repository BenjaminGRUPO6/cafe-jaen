import logging
from collections.abc import Sequence

from forecasting.domain.business_days import next_business_days
from forecasting.domain.errors import NotEnoughHistoryError
from forecasting.domain.forecast import Forecast
from forecasting.domain.metrics import mean_absolute_percentage_error
from forecasting.domain.ports.forecast_model import ForecastModel
from forecasting.domain.ports.forecast_repository import ForecastRepository
from shared.domain.ports.clock import Clock

logger = logging.getLogger(__name__)
MIN_TRAINING_POINTS = 60


class GenerateForecast:
    """HU06: elige el modelo con menor MAPE y pronostica los próximos días hábiles."""

    def __init__(
        self,
        models: Sequence[ForecastModel],
        repository: ForecastRepository,
        clock: Clock,
        horizon: int = 7,
        validation_days: int = 30,
    ) -> None:
        self._models = models
        self._repository = repository
        self._clock = clock
        self._horizon = horizon
        self._validation_days = validation_days

    def execute(self, history: Sequence[float]) -> Forecast:
        required = MIN_TRAINING_POINTS + self._validation_days
        if len(history) < required:
            raise NotEnoughHistoryError(required)

        best_model, best_mape = self._select_best_model(history)
        predictions = best_model.predict(history, self._horizon)
        today = self._clock.today()
        forecast = Forecast.from_predictions(
            generated_on=today,
            model_name=best_model.name,
            mape=best_mape,
            days=next_business_days(today, self._horizon),
            predictions=predictions,
        )
        self._repository.save(forecast)
        return forecast

    def _select_best_model(self, history: Sequence[float]) -> tuple[ForecastModel, float]:
        # Validación: se entrena sin los últimos días y se compara contra lo que realmente pasó
        training, actual = history[: -self._validation_days], history[-self._validation_days :]
        scores = []
        for model in self._models:
            mape = mean_absolute_percentage_error(actual, model.predict(training, len(actual)))
            logger.info("Modelo %s: MAPE %.2f %%", model.name, mape)
            scores.append((mape, model))
        best_mape, best_model = min(scores, key=lambda score: score[0])
        return best_model, best_mape
