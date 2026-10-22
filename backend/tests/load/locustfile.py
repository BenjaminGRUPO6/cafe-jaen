"""Prueba de carga (T32, PA-10-3): 30 caficultores usando la app a la vez.

Uso (con la API levantada y datos cargados):
    locust -f tests/load/locustfile.py --headless -u 30 -r 10 -t 60s --host http://localhost:8000
Cada usuario virtual necesita su propio código de invitación: LOAD-001 … LOAD-030
(los crea scripts/create_load_test_codes.py).
"""

import itertools

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
                "password": "carga2026!",
                "consent_accepted": True,
            },
        )
        self.client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

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
