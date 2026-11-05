"""Migración 0007: quita lo que generó la demostración y conserva todos los datos reales."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from shared.infrastructure import settings as settings_module

BACKEND = Path(__file__).parents[2]


@pytest.fixture
def database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    url = f"sqlite:///{tmp_path / 'migracion.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.chdir(BACKEND)
    settings_module.get_settings.cache_clear()
    yield url
    settings_module.get_settings.cache_clear()


def alembic(revision: str) -> None:
    command.upgrade(Config(str(BACKEND / "alembic.ini")), revision)


def test_only_synthetic_data_is_removed(database: str) -> None:
    alembic("0006")
    engine = create_engine(database)
    with engine.begin() as db:
        db.execute(
            text(
                "INSERT INTO live_quotes (quoted_at, cents_per_pound, sources) VALUES "
                "('2026-11-05 10:00', 395, 'DEMO A (sintético), DEMO C (sintético)'),"
                "('2026-11-05 10:01', 401, 'Yahoo Finance, Stooq')"
            )
        )
        db.execute(
            text(
                "INSERT INTO quotations (quoted_on, cents_per_pound, source) VALUES "
                "('2026-11-03', 390, 'DEMO (sintético)'), ('2026-11-04', 400, 'Yahoo Finance')"
            )
        )
        db.execute(
            text(
                "INSERT INTO exchange_rates (rated_on, soles_per_dollar, source) VALUES "
                "('2026-11-03', 3.7, 'DEMO (sintético)'), ('2026-11-04', 3.76, 'BCRP')"
            )
        )
        db.execute(
            text(
                "INSERT INTO local_price_observations "
                "(observed_at, cooperative, coffee_type, paid_soles, exchange_soles) VALUES "
                "('2026-11-04', 'Cooperativa Demo 1', 'convencional', 1080, 1500),"
                "('2026-11-04', 'Cooperativa Agraria Café del Norte', 'convencional', 1100, 1510)"
            )
        )
        db.execute(
            text("INSERT INTO cooperatives (name, location) VALUES ('Cooperativa Demo 2', 'x')")
        )
        db.execute(
            text(
                "INSERT INTO invitation_codes (code, used_by) VALUES "
                "('DEMO-0001', 'usuario-1'), ('DEMO-0002', NULL), ('JAEN-ABC123', NULL)"
            )
        )
        db.execute(
            text(
                "INSERT INTO price_collections (id, collected_at) VALUES "
                "(1, '2026-11-05 10:00'), (2, '2026-11-05 10:01')"
            )
        )
        db.execute(
            text(
                "INSERT INTO source_readings (collection_id, source, status) VALUES "
                "(1, 'DEMO A (sintético)', 'usada'), (2, 'Yahoo Finance', 'usada')"
            )
        )

    alembic("head")

    with engine.connect() as db:

        def column(sql: str) -> list[object]:
            return [row[0] for row in db.execute(text(sql))]

        assert column("SELECT sources FROM live_quotes") == ["Yahoo Finance, Stooq"]
        assert column("SELECT source FROM quotations") == ["Yahoo Finance"]
        assert column("SELECT source FROM exchange_rates") == ["BCRP"]
        assert column("SELECT cooperative FROM local_price_observations") == [
            "Cooperativa Agraria Café del Norte"
        ]
        assert not any("Demo" in str(n) for n in column("SELECT name FROM cooperatives"))
        assert "CENFROCAFE – Central Fronteriza del Norte de Cafetaleros" in column(
            "SELECT name FROM cooperatives"
        )
        assert sorted(column("SELECT code FROM invitation_codes")) == ["DEMO-0001", "JAEN-ABC123"]
        assert column("SELECT id FROM price_collections") == [2]
        assert column("SELECT source FROM source_readings") == ["Yahoo Finance"]
    engine.dispose()
