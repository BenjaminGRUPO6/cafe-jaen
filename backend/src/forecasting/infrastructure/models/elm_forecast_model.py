"""Extreme Learning Machine (ELM) para series de tiempo.

Sigue la idea de Deina et al. (2022): una red de una capa oculta cuyos pesos de
entrada son aleatorios y fijos; solo se calculan los pesos de salida con mínimos
cuadrados regularizados. Es rápida de entrenar y no necesita iteraciones.
"""

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


class ElmForecastModel:
    """Implementa ForecastModel con una ELM y pronóstico recursivo de varios pasos."""

    name = "elm"

    def __init__(
        self,
        window: int = 10,
        hidden_neurons: int = 40,
        regularization: float = 1e-3,
        seed: int = 42,
    ) -> None:
        self._window = window
        self._hidden = hidden_neurons
        self._regularization = regularization
        self._seed = seed  # semilla fija: resultados reproducibles para la tesis

    def predict(self, history: Sequence[float], horizon: int) -> list[float]:
        series = np.asarray(history, dtype=float)
        low, high = series.min(), series.max()
        scale = (high - low) or 1.0
        normalized = (series - low) / scale

        inputs, targets = self._sliding_windows(normalized)
        rng = np.random.default_rng(self._seed)
        input_weights = rng.uniform(-1, 1, size=(self._window, self._hidden))
        biases = rng.uniform(-1, 1, size=self._hidden)
        output_weights = self._fit_output_weights(
            self._hidden_layer(inputs, input_weights, biases), targets
        )

        # Pronóstico recursivo: cada predicción se usa como entrada del paso siguiente
        window = list(normalized[-self._window :])
        predictions: list[float] = []
        for _ in range(horizon):
            features = np.asarray(window[-self._window :]).reshape(1, -1)
            value = float((self._hidden_layer(features, input_weights, biases) @ output_weights)[0])
            predictions.append(value * scale + low)
            window.append(value)
        return predictions

    def _sliding_windows(
        self, series: NDArray[np.float64]
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        count = len(series) - self._window
        inputs = np.array([series[i : i + self._window] for i in range(count)])
        targets = series[self._window :]
        return inputs, targets

    @staticmethod
    def _hidden_layer(
        inputs: NDArray[np.float64], weights: NDArray[np.float64], biases: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        result: NDArray[np.float64] = 1.0 / (1.0 + np.exp(-(inputs @ weights + biases)))  # sigmoide
        return result

    def _fit_output_weights(
        self, hidden: NDArray[np.float64], targets: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        # Mínimos cuadrados con regularización de Tikhonov (ridge)
        identity = np.eye(hidden.shape[1])
        weights: NDArray[np.float64] = np.linalg.solve(
            hidden.T @ hidden + self._regularization * identity, hidden.T @ targets
        )
        return weights
