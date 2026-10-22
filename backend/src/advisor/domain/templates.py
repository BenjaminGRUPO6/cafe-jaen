"""Respuestas con plantilla: se construyen solo con los datos de los agentes.

Se usan cuando no hay LLM disponible y como respaldo si el LLM incluye un número
que no está en los datos (salvaguarda contra precios inventados, HU08).
"""

from datetime import datetime
from typing import Any

from advisor.domain.answer import NO_INFORMATION
from advisor.domain.formatting import percent, soles, spanish_date
from shared.domain.contract import Action

_COFFEE_NAMES = {"convencional": "convencional", "organico": "orgánico", "especial": "especial"}


def template_answer(action: str, data: dict[str, Any]) -> str:
    # Action es StrEnum: se puede buscar directamente con el texto de la acción
    builders = {
        Action.GET_LIVE_PRICE: _live_price,
        Action.GET_PRICE_HISTORY: _history,
        Action.GET_FORECAST: _forecast,
        Action.GET_SELLING_ADVICE: _selling_advice,
    }
    builder = builders.get(action)  # type: ignore[call-overload]
    return builder(data) if builder else NO_INFORMATION


def _live_price(data: dict[str, Any]) -> str:
    quoted_at = datetime.fromisoformat(data["quoted_at"])
    text = (
        f"En la bolsa de Nueva York el café está a {soles(data['cents_per_pound'])} centavos de "
        f"dólar por libra, que equivale a S/ {soles(data['price_soles'])} por quintal (46 kg) "
        f"(cotización de las {quoted_at:%H:%M} del {spanish_date(data['date'])})"
    )
    change = data.get("change_soles")
    if change:
        direction = "subió" if change > 0 else "bajó"
        change_pct = percent(abs(data["change_pct"]))
        text += f"; {direction} S/ {soles(abs(change))} ({change_pct} %) frente al cierre anterior"
    if not data.get("market_open", True):
        text += ". La bolsa está cerrada: es el último precio registrado"
    text += f". Fuente: {', '.join(data['sources'])}."
    estimates = data.get("local_estimates", [])
    if estimates:
        # HU12: lo que se paga en Jaén, calibrado con precios de cooperativas (versión corta)
        parts = [
            f"{_COFFEE_NAMES.get(e['coffee_type'], '')} S/ {soles(e['estimated_soles'])}"
            for e in estimates
        ]
        text += f" Precio estimado en Jaén: {'; '.join(parts)} (según precios de cooperativas)."
    return text


def _history(data: dict[str, Any]) -> str:
    points = data["points"]
    if not points:
        return "Todavía no hay precios registrados para ese periodo."
    prices = [p["price_soles"] for p in points]
    last = points[-1]
    if data.get("period") == "today":
        return (
            f"Hoy el precio estuvo entre S/ {soles(min(prices))} y S/ {soles(max(prices))} "
            f"por quintal; el último es S/ {soles(last['price_soles'])}. "
            "Fuente: bolsa de Nueva York."
        )
    first = points[0]
    return (
        f"Del {spanish_date(first['date'])} al {spanish_date(last['date'])} el precio estuvo entre "
        f"S/ {soles(min(prices))} y S/ {soles(max(prices))} por quintal. "
        f"El último cierre es S/ {soles(last['price_soles'])}. Fuente: bolsa de Nueva York y BCRP."
    )


def _forecast(data: dict[str, Any]) -> str:
    points = data["points"]
    last = points[-1]
    lowest = soles(min(p["lower_soles"] for p in points))
    highest = soles(max(p["upper_soles"] for p in points))
    return (
        f"Para los próximos días hábiles se espera que el precio esté entre S/ {lowest} "
        f"y S/ {highest} por quintal; para el {spanish_date(last['date'])} "
        f"se espera S/ {soles(last['expected_soles'])}. {data['disclaimer']}"
    )


def _selling_advice(data: dict[str, Any]) -> str:
    return f"{data['verdict']}. {data['reason']} {data['disclaimer']}"
