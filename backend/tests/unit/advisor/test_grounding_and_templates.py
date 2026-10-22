from advisor.domain.grounding import is_grounded
from advisor.domain.templates import template_answer

LIVE = {
    "quoted_at": "2026-11-04T08:55:00-05:00",
    "date": "2026-11-04",
    "cents_per_pound": 300.0,
    "price_soles": 1140.89,
    "previous_close_soles": 1100.0,
    "change_soles": 40.89,
    "change_pct": 3.72,
    "market_open": True,
    "stale": False,
    "sources": ["Yahoo Finance", "Stooq", "BCRP"],
}
ADVICE = {
    "verdict": "Esperar",
    "reason": (
        "El pronóstico indica que el precio podría subir de S/ 1140,89 a S/ 1190,00 por quintal "
        "(+4,3 %) hacia el 13/11, y aun en el peor caso estimado no bajaría del precio de hoy. "
        "Si puedes esperar, conviene esperar."
    ),
    "current_soles": 1140.89,
    "target_date": "2026-11-13",
    "target_soles": 1190.0,
    "change_pct": 4.3,
    "hit_rate_pct": None,
    "disclaimer": "Recomendación referencial: la decisión de vender siempre es tuya.",
    "sources": ["Bolsa de Nueva York (ICE)", "Pronóstico del Agente Predictor"],
}


def test_template_for_live_price_uses_only_data() -> None:
    text = template_answer("get_live_price", LIVE)

    assert text == (
        "En la bolsa de Nueva York el café está a 300,00 centavos de dólar por libra, que equivale "
        "a S/ 1140,89 por quintal (46 kg) (cotización de las 08:55 del 04/11/2026); subió "
        "S/ 40,89 (3,7 %) frente al cierre anterior. Fuente: Yahoo Finance, Stooq, BCRP."
    )
    assert is_grounded(text, LIVE)


def test_live_price_template_adds_estimate_for_jaen() -> None:
    estimate = {
        "coffee_type": "convencional",
        "estimated_soles": 900.7,
        "ratio_pct": 78.9,
        "observations": 3,
        "first_day": "2026-11-02",
        "last_day": "2026-11-04",
        "few_data": False,
    }
    data = {**LIVE, "local_estimates": [estimate]}

    text = template_answer("get_live_price", data)

    assert text.endswith(
        "Precio estimado en Jaén: convencional S/ 900,70 (según precios de cooperativas)."
    )
    assert is_grounded(text, data)


def test_live_price_template_warns_when_market_is_closed() -> None:
    assert "La bolsa está cerrada" in template_answer(
        "get_live_price", {**LIVE, "market_open": False}
    )


def test_detects_invented_price() -> None:
    assert not is_grounded("El quintal está a S/ 1250,00 hoy.", LIVE)


def test_accepts_thousands_separator_written_by_llm() -> None:
    assert is_grounded("Hoy el quintal está a S/ 1.140,89.", LIVE)


def test_selling_advice_template_keeps_reason_and_disclaimer() -> None:
    text = template_answer("get_selling_advice", ADVICE)

    assert text.startswith("Esperar. El pronóstico indica")
    assert text.endswith("la decisión de vender siempre es tuya.")
    assert is_grounded(text, ADVICE)


def test_today_history_template() -> None:
    data = {
        "period": "today",
        "points": [
            {"time": "2026-11-04T08:55:00-05:00", "date": "2026-11-04", "price_soles": 1140.89},
            {"time": "2026-11-04T09:00:00-05:00", "date": "2026-11-04", "price_soles": 1142.1},
        ],
    }

    text = template_answer("get_price_history", data)

    assert text.startswith("Hoy el precio estuvo entre S/ 1140,89 y S/ 1142,10")
    assert is_grounded(text, data)


def test_unknown_action_returns_no_information() -> None:
    assert template_answer("bailar", {}).startswith("No tengo esa información")
