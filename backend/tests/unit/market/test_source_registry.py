"""QUOTATION_SOURCES mal escrito no debe impedir que la app arranque."""

from market.infrastructure.sources.registry import build_sources

DEFAULT = ["Yahoo Finance", "CNBC", "TradingView"]


def names(configured: list[str], stooq_key: str = "") -> list[str]:
    return [source.name for source in build_sources(configured, "Europe/Warsaw", stooq_key)]


def test_builds_the_configured_real_webs() -> None:
    assert names(["yahoo", "cnbc"]) == ["Yahoo Finance", "CNBC"]


def test_unknown_names_are_ignored() -> None:
    assert names(["demo", "cnbc", "cnbc"]) == ["CNBC"]


def test_without_valid_webs_uses_the_default_real_webs() -> None:
    assert names(["demo"]) == DEFAULT
    assert names([]) == DEFAULT


def test_stooq_is_only_used_with_its_api_key() -> None:
    # Desde 2026 Stooq no entrega datos sin clave
    assert names(["yahoo", "stooq"]) == ["Yahoo Finance"]
    assert names(["yahoo", "stooq"], stooq_key="clave") == ["Yahoo Finance", "Stooq"]
