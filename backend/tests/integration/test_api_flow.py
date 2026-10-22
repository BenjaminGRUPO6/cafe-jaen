"""Flujo completo por HTTP.

Registro → precio en vivo → gráfico → flujo en vivo → ciclo diario → pronóstico →
recomendación de venta → asesor.
"""

import json

from fastapi.testclient import TestClient

from tests.conftest import INVITATION_CODE


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_prices_require_session(client: TestClient) -> None:
    assert client.get("/api/prices/live").status_code == 401
    assert client.get("/api/decision/today").status_code == 401


def test_register_with_invalid_code_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "invitation_code": "NO-EXISTE",
            "phone": "987654321",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )

    assert response.status_code == 400
    assert "código" in response.json()["detail"]


def test_code_can_only_be_used_once(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "invitation_code": INVITATION_CODE,
            "phone": "911111111",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )

    assert response.status_code == 400


def test_login(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert (
        client.post(
            "/api/auth/login", json={"phone": "987654321", "password": "cafe2026!"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/auth/login", json={"phone": "987654321", "password": "otra-clave"}
        ).status_code
        == 401
    )


def test_live_price_and_history(client: TestClient, auth_headers: dict[str, str]) -> None:
    live = client.get("/api/prices/live", headers=auth_headers).json()
    history = client.get("/api/prices/history?period=90", headers=auth_headers).json()
    today = client.get("/api/prices/history?period=today", headers=auth_headers).json()

    # Sin cotizaciones en vivo todavía: se muestra el último cierre
    assert live["unit"] == "S/ por quintal (46 kg)" and live["price_soles"] > 0
    assert len(history["points"]) > 50
    assert today == {"period": "today", "points": []}


def test_history_only_accepts_known_periods(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/api/prices/history?period=45", headers=auth_headers).status_code == 422


def test_stream_sends_live_price_as_server_sent_event(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/api/prices/stream", headers=auth_headers)

    assert response.headers["content-type"].startswith("text/event-stream")
    event, data = response.text.strip().split("\n")
    assert event == "event: price"
    assert json.loads(data.removeprefix("data: "))["price_soles"] > 0


def test_daily_cycle_collects_and_forecasts(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert (
        client.get("/api/forecast", headers=auth_headers).status_code == 503
    )  # aún no hay pronóstico

    report = client.app.state.daily_cycle.execute()  # type: ignore[attr-defined]
    forecast = client.get("/api/forecast", headers=auth_headers).json()
    live = client.get("/api/prices/live", headers=auth_headers).json()
    today = client.get("/api/prices/history?period=today", headers=auth_headers).json()

    assert report.collection["quotation_saved"] and report.forecast_generated
    assert report.collection["sources_ok"] == ["Yahoo Finance", "Stooq"]
    assert len(forecast["points"]) == 7 and forecast["model"] in {"elm", "naive_drift"}
    assert live["price_soles"] == 1140.89  # consenso de 300 ¢/lb con TC 3,75
    assert live["sources"] == ["Yahoo Finance", "Stooq", "BCRP"]
    assert len(today["points"]) == 1


def test_selling_advice_after_daily_cycle(client: TestClient, auth_headers: dict[str, str]) -> None:
    # PA-05-*: antes del pronóstico no recomienda; después da una de las tres respuestas
    before = client.get("/api/decision/today", headers=auth_headers).json()
    client.app.state.daily_cycle.execute()  # type: ignore[attr-defined]
    after = client.get("/api/decision/today", headers=auth_headers).json()

    assert before["verdict"] == "Sin datos suficientes"
    assert after["verdict"] in {"Vender ahora", "Esperar", "Sin señal clara"}
    assert after["reason"] and "decisión de vender" in after["disclaimer"]


def test_only_the_team_can_record_cooperative_prices(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    # PA-12-1 y PA-12-2 (HU12)
    body = {"cooperative": "Coop. A", "coffee_type": "convencional", "paid_soles": 900}

    as_farmer = client.post("/api/admin/local-prices", json=body, headers=auth_headers)
    recorded = client.post("/api/admin/local-prices", json=body, headers=admin_headers)
    mistyped = client.post(
        "/api/admin/local-prices", json={**body, "paid_soles": 90}, headers=admin_headers
    )
    listed = client.get("/api/admin/local-prices", headers=admin_headers).json()
    live = client.get("/api/prices/live", headers=auth_headers).json()

    assert as_farmer.status_code == 403
    assert recorded.status_code == 201 and recorded.json()["cooperative"] == "Coop. A"
    assert mistyped.status_code == 400 and "bien escrito" in mistyped.json()["detail"]
    assert len(listed["observations"]) == 1
    assert live["local_estimates"][0]["coffee_type"] == "convencional"
    assert live["local_estimates"][0]["estimated_soles"] == 900.0


def test_advisor_answers_with_the_same_price_as_home(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # PA-08-1
    live = client.get("/api/prices/live", headers=auth_headers).json()
    reply = client.post(
        "/api/advisor/ask",
        json={"question": "¿A cuánto está el quintal hoy?"},
        headers=auth_headers,
    ).json()

    assert f"{live['price_soles']:.2f}".replace(".", ",") in reply["answer"]
    assert reply["used_tool"] == "get_live_price"
