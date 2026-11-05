"""La API entrega la app compilada en el despliegue de un solo servicio (Render)."""

import asyncio
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from shared.infrastructure.api.spa import SinglePageApp, mount_single_page_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    (tmp_path / "index.html").write_text("<html>Café Jaén</html>", encoding="utf-8")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('ok')", encoding="utf-8")
    app = FastAPI()

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    mount_single_page_app(app, str(tmp_path))
    return TestClient(app)


def test_serves_index_at_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Café Jaén" in response.text


def test_serves_static_assets(client: TestClient) -> None:
    assert client.get("/assets/app.js").text == "console.log('ok')"


def test_frontend_routes_fall_back_to_index(client: TestClient) -> None:
    response = client.get("/decision")

    assert response.status_code == 200
    assert "Café Jaén" in response.text


def test_api_routes_keep_priority(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_unknown_api_route_is_not_the_app(client: TestClient) -> None:
    assert client.get("/api/no-existe").status_code == 404


def test_missing_build_fails_with_clear_message(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="compila el front-end"):
        mount_single_page_app(FastAPI(), str(tmp_path))


@pytest.mark.parametrize("path", ["api/no-existe", "api\\no-existe", "api"])
def test_api_paths_are_rejected_on_any_platform(tmp_path: Path, path: str) -> None:
    # En Windows Starlette entrega «api\\no-existe»; en Linux, «api/no-existe»
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    app = SinglePageApp(directory=tmp_path, html=True)
    scope = {"type": "http", "method": "GET", "headers": []}

    with pytest.raises(HTTPException) as error:
        asyncio.run(app.get_response(path, scope))

    assert error.value.status_code == 404
