from collections.abc import Sequence


class NaiveDriftForecastModel:
    """Modelo base: último valor más la tendencia promedio (método ingenuo con deriva).

    Sirve de referencia: el ELM solo se usa si lo supera.
    """

    name = "naive_drift"

    def predict(self, history: Sequence[float], horizon: int) -> list[float]:
        if len(history) < 2:
            return [history[-1]] * horizon
        drift = (history[-1] - history[0]) / (len(history) - 1)
        return [history[-1] + drift * step for step in range(1, horizon + 1)]
