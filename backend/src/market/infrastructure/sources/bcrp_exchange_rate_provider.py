"""Tipo de cambio desde la API de series estadísticas del BCRP.

Documentación: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
"""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import ExchangeRate

BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
DEFAULT_SERIES = "PD04640PD"  # tipo de cambio interbancario, venta (S/ por US$)
SOURCE = "BCRP"
_SPANISH_MONTHS = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}  # fmt: skip


class BcrpExchangeRateProvider:
    """Implementa ExchangeRateProvider consultando la API del BCRP."""

    def __init__(self, series: str = DEFAULT_SERIES, timeout_seconds: float = 10.0) -> None:
        self._series = series
        self._timeout = timeout_seconds

    def fetch_latest(self) -> ExchangeRate:
        today = date.today()
        rates = self.fetch_history(today - timedelta(days=15), today)
        if not rates:
            raise SourceUnavailableError("El BCRP no publicó tipo de cambio en los últimos días")
        return rates[-1]

    def fetch_history(self, start: date, end: date) -> list[ExchangeRate]:
        url = f"{BASE_URL}/{self._series}/json/{start.isoformat()}/{end.isoformat()}"
        try:
            response = httpx.get(url, timeout=self._timeout)
            response.raise_for_status()
            return parse_bcrp_response(response.json())
        except (httpx.HTTPError, ValueError) as error:
            raise SourceUnavailableError(f"El BCRP no respondió: {error}") from error


def parse_bcrp_response(payload: dict[str, Any]) -> list[ExchangeRate]:
    """Convierte la respuesta JSON del BCRP en tipos de cambio (ignora días sin dato)."""
    rates: list[ExchangeRate] = []
    for period in payload.get("periods", []):
        rated_on = _parse_bcrp_date(period["name"])
        try:
            value = Decimal(period["values"][0])
        except (InvalidOperation, IndexError):
            continue  # el BCRP publica "n.d." los días sin dato
        rates.append(ExchangeRate(value, rated_on, SOURCE))
    return rates


def _parse_bcrp_date(name: str) -> date:
    """El BCRP nombra los días así: «21.Oct.25»."""
    day, month, year = name.split(".")
    return date(2000 + int(year), _SPANISH_MONTHS[month], int(day))
