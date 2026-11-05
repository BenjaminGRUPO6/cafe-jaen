"""La URL de PostgreSQL que entrega Neon (o Render) se acepta tal cual."""

import pytest

from shared.infrastructure.settings import Settings


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@host/db", "postgresql+psycopg2://u:p@host/db"),
        (
            "postgresql://u:p@ep.neon.tech/db?sslmode=require",
            "postgresql+psycopg2://u:p@ep.neon.tech/db?sslmode=require",
        ),
        ("postgresql+psycopg2://u:p@host/db", "postgresql+psycopg2://u:p@host/db"),
        ("sqlite:///./cafe_jaen.db", "sqlite:///./cafe_jaen.db"),
    ],
)
def test_database_url_uses_the_psycopg2_driver(given: str, expected: str) -> None:
    assert Settings(database_url=given).database_url == expected
