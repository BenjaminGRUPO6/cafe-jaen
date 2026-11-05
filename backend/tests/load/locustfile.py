"""Prueba de carga (T32, PA-10-3): 30 caficultores usando la app a la vez.

Uso (con la API levantada y datos cargados):
    locust -f tests/load/locustfile.py --headless -u 30 -r 10 -t 60s --host http://localhost:8000
Cada usuario virtual necesita su propio código de invitación: LOAD-001 … LOAD-030
(los crea scripts/create_load_test_codes.py).
Desde v1.10 la cuenta se activa con el código del correo: el usuario virtual lo lee como lo haría
el equipo, en «Participantes», con la cuenta de ADMIN_PHONE y ADMIN_PASSWORD.
"""

import itertools
import os

from locust import HttpUser, between, task

_codes = itertools.count(1)


class CoffeeGrower(HttpUser):
    """Simula a un caficultor: mira el precio a menudo y a veces consulta lo demás."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        number = next(_codes)
        response = self.client.post(
            "/api/auth/register",
            json={
                "invitation_code": f"LOAD-{number:03d}",
                "phone": f"9{number:08d}",
                "email": f"carga{number:03d}@example.com",
                "password": "carga2026!",
                "consent_accepted": True,
            },
        )
        phone = response.json()["phone"]
        admin = self.client.post(
            "/api/auth/login",
            json={"phone": os.environ["ADMIN_PHONE"], "password": os.environ["ADMIN_PASSWORD"]},
        ).json()["access_token"]
        participants = self.client.get(
            "/api/admin/participants", headers={"Authorization": f"Bearer {admin}"}
        ).json()["participants"]
        code = next(p["pending_code"] for p in participants if p["phone"] == phone)
        session = self.client.post("/api/auth/verify", json={"phone": phone, "code": code})
        self.client.headers["Authorization"] = f"Bearer {session.json()['access_token']}"

    @task(5)
    def live_price(self) -> None:
        self.client.get("/api/prices/live")

    @task(2)
    def history(self) -> None:
        self.client.get("/api/prices/history?period=today")

    @task(2)
    def forecast(self) -> None:
        self.client.get("/api/forecast")

    @task(1)
    def selling_advice(self) -> None:
        self.client.get("/api/decision/today")

    @task(1)
    def advisor(self) -> None:
        self.client.post("/api/advisor/ask", json={"question": "¿A cuánto está el quintal hoy?"})
