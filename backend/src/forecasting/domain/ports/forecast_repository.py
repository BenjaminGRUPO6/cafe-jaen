from typing import Protocol

from forecasting.domain.forecast import Forecast


class ForecastRepository(Protocol):
    def save(self, forecast: Forecast) -> None: ...

    def latest(self) -> Forecast | None: ...
