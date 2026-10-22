"""Salvaguarda: verifica que todos los números de una respuesta salgan de los datos."""

import json
import re
from typing import Any

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_TOLERANCE = 0.06  # admite redondeos a un decimal (p. ej., 3,72 % mostrado como 3,7 %)
_ALWAYS_ALLOWED = {46.0, 7.0}  # kg por quintal y horizonte del pronóstico


def is_grounded(text: str, data: dict[str, Any]) -> bool:
    allowed = _numbers_in_data(data) | _ALWAYS_ALLOWED
    return all(
        any(abs(number - value) <= _TOLERANCE for value in allowed)
        for number in _numbers_in_text(text)
    )


def _numbers_in_data(data: dict[str, Any]) -> set[float]:
    numbers = {float(token) for token in re.findall(r"-?\d+(?:\.\d+)?", json.dumps(data))}
    return numbers | {abs(n) for n in numbers}


def _numbers_in_text(text: str) -> list[float]:
    return [_to_float(token) for token in _NUMBER.findall(text)]


def _to_float(token: str) -> float:
    # «1.140,89» o «1140,89» → 1140.89 ; «3.7» → 3.7
    if "," in token:
        token = token.replace(".", "").replace(",", ".")
    elif token.count(".") > 1:
        token = token.replace(".", "")
    return float(token)
