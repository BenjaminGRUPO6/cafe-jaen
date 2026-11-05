"""QUOTATION_SOURCES mal escrito no debe impedir que la app arranque."""

from market.infrastructure.sources.registry import build_sources


def names(configured: list[str]) -> list[str]:
    return [source.name for source in build_sources(configured, "Europe/Warsaw")]


def test_builds_the_configured_real_webs() -> None:
    assert names(["yahoo", "stooq"]) == ["Yahoo Finance", "Stooq"]
    assert names(["stooq"]) == ["Stooq"]


def test_unknown_names_are_ignored() -> None:
    assert names(["demo", "stooq", "stooq"]) == ["Stooq"]


def test_without_valid_webs_uses_yahoo_and_stooq() -> None:
    assert names(["demo"]) == ["Yahoo Finance", "Stooq"]
    assert names([]) == ["Yahoo Finance", "Stooq"]
