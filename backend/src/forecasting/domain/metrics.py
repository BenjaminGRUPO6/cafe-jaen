from collections.abc import Sequence


def mean_absolute_percentage_error(actual: Sequence[float], predicted: Sequence[float]) -> float:
    """MAPE en porcentaje: promedio de |real − predicho| / real × 100."""
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Las series deben tener la misma longitud y no estar vacías")
    errors = [abs(a - p) / abs(a) for a, p in zip(actual, predicted, strict=True) if a != 0]
    return 100 * sum(errors) / len(errors)
