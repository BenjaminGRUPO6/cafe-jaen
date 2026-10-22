from collections.abc import Sequence
from typing import Protocol


class ForecastModel(Protocol):
    """Puerto de salida: un modelo que pronostica los siguientes `horizon` valores."""

    @property
    def name(self) -> str: ...

    def predict(self, history: Sequence[float], horizon: int) -> list[float]: ...
