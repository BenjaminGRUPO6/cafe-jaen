"""Flujo completo por HTTP.

Registro → precio en vivo → gráfico → flujo en vivo → ciclo diario → pronóstico →
recomendación de venta → asesor.
"""

import json

from fastapi.testclient import TestClient

from tests.conftest import INVITATION_CODE
from tests.fakes import FakeCodeSender


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
            "email": "caficultor@gmail.com",
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
            "email": "otro@gmail.com",
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


def test_team_sees_participants_and_their_last_login(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    client.post("/api/auth/login", json={"phone": "987654321", "password": "cafe2026!"})

    response = client.get("/api/admin/participants", headers=admin_headers)

    body = response.json()
    assert response.status_code == 200
    farmer = next(p for p in body["participants"] if p["phone"] == "987654321")
    assert farmer["role"] == "farmer"
    assert farmer["invitation_code"] == INVITATION_CODE
    assert farmer["last_login_at"] is not None
    admin = next(p for p in body["participants"] if p["phone"] == "911111111")
    assert admin["role"] == "admin"
    assert admin["invitation_code"] is None
    assert body["codes"] == {"total": 1, "used": 1}


def test_farmers_cannot_see_participants(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.get("/api/admin/participants", headers=auth_headers).status_code == 403


def test_team_generates_codes_that_farmers_can_use(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/admin/invitation-codes", json={"count": 2}, headers=admin_headers
    ).json()["codes"]

    registered = client.post(
        "/api/auth/register",
        json={
            "invitation_code": created[0],
            "phone": "955444333",
            "email": "nuevo@gmail.com",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )
    listed = client.get("/api/admin/invitation-codes", headers=admin_headers).json()["codes"]

    assert registered.status_code == 201
    status = {c["code"]: c["used"] for c in listed}
    assert status[created[0]] is True
    assert status[created[1]] is False
    assert listed[0]["used"] is False  # los libres primero


def test_invalid_amount_of_codes_is_rejected(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/admin/invitation-codes", json={"count": 500}, headers=admin_headers
    )

    assert response.status_code == 400


def test_farmers_cannot_generate_codes(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/api/admin/invitation-codes", json={"count": 1}, headers=auth_headers)

    assert response.status_code == 403


def test_farmers_see_what_each_cooperative_paid(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    client.post(
        "/api/admin/local-prices",
        json={"cooperative": "CENFROCAFE", "coffee_type": "convencional", "paid_soles": 1100},
        headers=admin_headers,
    )

    body = client.get("/api/prices/local", headers=auth_headers).json()

    assert body["observations"][0]["cooperative"] == "CENFROCAFE"
    assert client.get("/api/prices/live", headers=auth_headers).json()["exchange_rate"] == 3.75


def test_team_manages_the_cooperative_catalog(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/admin/cooperatives",
        headers=admin_headers,
        json={"name": "Cooperativa Agraria Café del Norte", "website": "https://cafe.pe"},
    )
    assert created.status_code == 201
    new_id = created.json()["id"]
    duplicate = client.post(
        "/api/admin/cooperatives", headers=admin_headers, json={"name": "cenfrocafe"}
    )
    assert duplicate.status_code == 400

    renamed = client.put(
        f"/api/admin/cooperatives/{new_id}",
        headers=admin_headers,
        json={"name": "Café del Norte", "location": "Jaén", "active": True},
    )
    assert renamed.json()["name"] == "Café del Norte"
    visible = client.get("/api/cooperatives", headers=auth_headers).json()["cooperatives"]
    assert "Café del Norte" in {c["name"] for c in visible}

    removed = client.delete(f"/api/admin/cooperatives/{new_id}", headers=admin_headers)
    assert removed.json() == {"result": "deleted"}
    assert client.get("/api/admin/cooperatives", headers=auth_headers).status_code == 403


def test_team_corrects_and_deletes_a_price(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    saved = client.post(
        "/api/admin/local-prices",
        headers=admin_headers,
        json={"cooperative": "Coop. A", "coffee_type": "convencional", "paid_soles": 900},
    ).json()

    corrected = client.patch(
        f"/api/admin/local-prices/{saved['id']}", headers=admin_headers, json={"paid_soles": 950}
    )
    assert corrected.status_code == 200 and corrected.json()["ratio_pct"] > saved["ratio_pct"]
    assert (
        client.delete(f"/api/admin/local-prices/{saved['id']}", headers=admin_headers).status_code
        == 204
    )
    assert (
        client.delete(f"/api/admin/local-prices/{saved['id']}", headers=admin_headers).status_code
        == 404
    )
    archived = client.delete("/api/admin/cooperatives/1", headers=admin_headers)
    assert archived.json() == {"result": "deleted"}  # ya no le quedan precios


def test_team_sees_the_price_log(client: TestClient, admin_headers: dict[str, str]) -> None:
    client.app.state.daily_cycle.execute()  # type: ignore[attr-defined]

    entries = client.get("/api/admin/price-log", headers=admin_headers).json()["entries"]

    assert entries and entries[0]["cents_per_pound"] == 300.0
    assert entries[0]["sources"] == ["Yahoo Finance", "Stooq"]
    # Cada consulta guarda lo que marcó cada web, para entender por qué se publicó ese precio
    readings = entries[0]["readings"]
    assert [(r["source"], r["status"]) for r in readings] == [
        ("Yahoo Finance", "usada"),
        ("Stooq", "usada"),
    ]
    assert entries[0]["median_cents"] == 300.0


def test_team_deletes_only_unused_invitation_codes(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    (code,) = client.post(
        "/api/admin/invitation-codes", headers=admin_headers, json={"count": 1}
    ).json()["codes"]

    assert (
        client.delete(f"/api/admin/invitation-codes/{code}", headers=admin_headers).status_code
        == 204
    )
    assert (
        client.delete(f"/api/admin/invitation-codes/{code}", headers=admin_headers).status_code
        == 404
    )
    used = client.delete(f"/api/admin/invitation-codes/{INVITATION_CODE}", headers=admin_headers)
    assert used.status_code == 409


def test_registration_needs_the_code_before_entering(
    client: TestClient, code_outbox: FakeCodeSender, admin_headers: dict[str, str]
) -> None:
    (code,) = client.post(
        "/api/admin/invitation-codes", json={"count": 1}, headers=admin_headers
    ).json()["codes"]
    body = {
        "invitation_code": code,
        "phone": "944555666",
        "email": "maria@gmail.com",
        "password": "cafe2026!",
        "consent_accepted": True,
    }

    registered = client.post("/api/auth/register", json=body).json()
    blocked = client.post("/api/auth/login", json={"phone": "944555666", "password": "cafe2026!"})
    participants = client.get("/api/admin/participants", headers=admin_headers).json()
    pending = next(p for p in participants["participants"] if p["phone"] == "944555666")
    verified = client.post(
        "/api/auth/verify", json={"phone": "944555666", "code": code_outbox.last_code()}
    )

    assert registered == {
        "verification_required": True,
        "phone": "944555666",
        "email": "ma***@gmail.com",
        "delivered_by": "whatsapp",
        "team_whatsapp": None,
    }
    assert blocked.status_code == 403 and blocked.json()["phone"] == "944555666"
    assert pending["verified"] is False and pending["pending_code"] == code_outbox.last_code()
    assert verified.status_code == 200 and "access_token" in verified.json()


def test_team_creates_team_codes_and_deletes_accounts(
    client: TestClient,
    code_outbox: FakeCodeSender,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
) -> None:
    (team_code,) = client.post(
        "/api/admin/invitation-codes", json={"count": 1, "role": "admin"}, headers=admin_headers
    ).json()["codes"]
    client.post(
        "/api/auth/register",
        json={
            "invitation_code": team_code,
            "phone": "933222111",
            "email": "jhon@gmail.com",
            "password": "equipo2026!",
            "consent_accepted": True,
        },
    )
    token = client.post(
        "/api/auth/verify", json={"phone": "933222111", "code": code_outbox.last_code()}
    ).json()["access_token"]
    second_admin = {"Authorization": f"Bearer {token}"}
    farmer = next(
        p
        for p in client.get("/api/admin/participants", headers=second_admin).json()["participants"]
        if p["phone"] == "987654321"
    )

    deleted = client.delete(f"/api/admin/participants/{farmer['id']}", headers=second_admin)

    assert team_code.startswith("EQUIPO-")
    assert deleted.status_code == 204
    # La sesión de la cuenta eliminada deja de servir y su código vuelve a estar libre
    assert client.get("/api/prices/live", headers=auth_headers).status_code == 401
    codes = client.get("/api/admin/invitation-codes", headers=second_admin).json()["codes"]
    assert next(c for c in codes if c["code"] == INVITATION_CODE)["used"] is False


def test_email_is_optional_and_works_to_log_in(
    client: TestClient, code_outbox: FakeCodeSender, admin_headers: dict[str, str]
) -> None:
    codes = client.post(
        "/api/admin/invitation-codes", json={"count": 2}, headers=admin_headers
    ).json()["codes"]
    without_email = client.post(
        "/api/auth/register",
        json={
            "invitation_code": codes[0],
            "phone": "922333444",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )
    client.post(
        "/api/auth/register",
        json={
            "invitation_code": codes[1],
            "phone": "922333555",
            "email": "rosa@gmail.com",
            "password": "cafe2026!",
            "consent_accepted": True,
        },
    )
    client.post("/api/auth/verify", json={"phone": "922333555", "code": code_outbox.last_code()})

    by_email = client.post(
        "/api/auth/login", json={"identifier": "Rosa@Gmail.com", "password": "cafe2026!"}
    )
    by_phone = client.post(
        "/api/auth/login", json={"identifier": "922333555", "password": "cafe2026!"}
    )

    assert without_email.status_code == 201 and without_email.json()["email"] is None
    assert by_email.status_code == 200 and by_phone.status_code == 200


def test_farmers_write_to_the_team_and_read_the_answer(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    sent = client.post(
        "/api/support/messages",
        json={"text": "¿Cada cuánto cambia el precio?"},
        headers=auth_headers,
    )
    inbox = client.get("/api/admin/support", headers=admin_headers).json()
    thread = inbox["threads"][0]
    client.get(f"/api/admin/support/{thread['user_id']}", headers=admin_headers)
    client.post(
        f"/api/admin/support/{thread['user_id']}",
        json={"text": "Cada minuto con la bolsa abierta."},
        headers=admin_headers,
    )

    assert sent.status_code == 201
    assert inbox["unread"] == 1 and thread["user"]["phone"] == "987654321"
    assert client.get("/api/support/unread", headers=auth_headers).json() == {"unread": 1}
    messages = client.get("/api/support/messages", headers=auth_headers).json()["messages"]
    assert [m["author"] for m in messages] == ["farmer", "team"]
    assert client.get("/api/admin/support", headers=auth_headers).status_code == 403


def test_team_creates_team_accounts_and_everyone_sees_their_profile(
    client: TestClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/admin/team",
        json={"name": "Jhon Chávez", "phone": "955000111", "password": "equipo2026!"},
        headers=admin_headers,
    )
    token = client.post(
        "/api/auth/login", json={"identifier": "955000111", "password": "equipo2026!"}
    ).json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    farmer = client.get("/api/auth/me", headers=auth_headers).json()

    assert created.status_code == 201
    assert (me["display_name"], me["role"]) == ("Jhon Chávez", "admin")
    assert (farmer["role"], farmer["phone"]) == ("farmer", "987654321")
    assert (
        client.post(
            "/api/admin/team",
            json={"name": "X", "phone": "955000222", "password": "equipo2026!"},
            headers=auth_headers,
        ).status_code
        == 403
    )
