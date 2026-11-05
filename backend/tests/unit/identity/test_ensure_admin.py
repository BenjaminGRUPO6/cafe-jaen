"""scripts/ensure_admin.py: crea la cuenta del equipo en Render desde variables de entorno."""

import importlib.util
from pathlib import Path

import pytest

from identity.domain.phone_number import PhoneNumber
from identity.infrastructure.persistence.sqlalchemy_repositories import SqlAlchemyUserRepository
from shared.infrastructure import settings as settings_module
from shared.infrastructure.database import create_db_engine, create_session_factory, metadata

SCRIPT = Path(__file__).parents[3] / "scripts" / "ensure_admin.py"


def run_script(monkeypatch: pytest.MonkeyPatch, database_url: str, **env: str) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    for key in ("ADMIN_PHONE", "ADMIN_PASSWORD"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    settings_module.get_settings.cache_clear()
    spec = importlib.util.spec_from_file_location("ensure_admin", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()
    settings_module.get_settings.cache_clear()


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    url = f"sqlite:///{tmp_path / 'admin.db'}"
    metadata.create_all(create_db_engine(url))
    return url


def users(url: str) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(create_session_factory(create_db_engine(url)))


def test_creates_the_team_account_once(
    monkeypatch: pytest.MonkeyPatch, database_url: str, capsys: pytest.CaptureFixture[str]
) -> None:
    env = {"ADMIN_PHONE": "911222333", "ADMIN_PASSWORD": "equipo2026!"}

    run_script(monkeypatch, database_url, **env)
    run_script(monkeypatch, database_url, **env)

    admin = users(database_url).get_by_phone(PhoneNumber("911222333"))
    assert admin is not None and admin.role == "admin"
    output = capsys.readouterr().out
    assert "creada" in output and "ya existe" in output
    assert "equipo2026!" not in output


@pytest.mark.parametrize(
    "env",
    [{}, {"ADMIN_PHONE": "911222333", "ADMIN_PASSWORD": "corta"}],
)
def test_does_nothing_without_valid_variables(
    monkeypatch: pytest.MonkeyPatch, database_url: str, env: dict[str, str]
) -> None:
    run_script(monkeypatch, database_url, **env)

    assert users(database_url).get_by_phone(PhoneNumber("911222333")) is None
