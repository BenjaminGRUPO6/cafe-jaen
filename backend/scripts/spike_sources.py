"""Spike T01: compara varias webs del precio de la bolsa de Nueva York (KC) desde esta máquina.

Consulta cada fuente cada minuto durante N minutos y muestra, por fuente: precio, hora de la
cotización, retraso frente a la hora actual y diferencia con la mediana. Así se eligen las
fuentes (QUOTATION_SOURCES) y se mide el «tiempo real» que de verdad se puede ofrecer.

Uso:  python scripts/spike_sources.py --minutes 60      (con la bolsa abierta)
Copiar la salida en docs/xp/iteracion-0/spike.md (sección «Resultados»).
"""

import argparse
import time
from collections.abc import Callable
from datetime import date, datetime, timedelta
from decimal import Decimal
from statistics import median
from typing import Any
from zoneinfo import ZoneInfo

from market.domain.errors import SourceUnavailableError
from market.domain.quotation import LiveQuote
from market.infrastructure.sources.bcrp_exchange_rate_provider import BcrpExchangeRateProvider
from market.infrastructure.sources.stooq_quotation_source import StooqQuotationSource
from market.infrastructure.sources.yahoo_quotation_source import YahooQuotationSource
from shared.infrastructure.settings import get_settings

LIMA = ZoneInfo("America/Lima")


def check(name: str, probe: Callable[[], Any]) -> None:
    started = time.perf_counter()
    try:
        result = probe()
        print(f"[OK]    {name} ({time.perf_counter() - started:.1f} s): {result}")
    except Exception as error:  # el spike solo informa: no corrige nada
        print(f"[FALLA] {name}: {error}")


def compare_sources(minutes: int) -> None:
    settings = get_settings()
    sources = [YahooQuotationSource(), StooqQuotationSource(timezone=settings.stooq_timezone)]
    print(
        f"\n{'Hora Lima':<10}{'Fuente':<16}{'¢/lb':>10}{'Cotización':>18}{'Retraso':>10}{'Dif.':>8}"
    )
    for _ in range(minutes):
        now = datetime.now(LIMA)
        quotes: list[LiveQuote] = []
        for source in sources:
            try:
                quotes.append(source.fetch_latest())
            except SourceUnavailableError as error:
                print(f"{now:%H:%M:%S}  {source.name:<16}FALLA: {error}")
        middle = Decimal(median(q.cents_per_pound for q in quotes)) if quotes else None
        for quote in quotes:
            delay = (now - quote.quoted_at).total_seconds() / 60
            diff = (quote.cents_per_pound - middle) / middle * 100 if middle else Decimal(0)
            print(
                f"{now:%H:%M:%S}  {quote.sources[0]:<16}{quote.cents_per_pound:>10}"
                f"{quote.quoted_at.astimezone(LIMA):%d/%m %H:%M:%S}".rjust(18)
                + f"{delay:>8.1f} m{diff:>7.2f} %"
            )
        time.sleep(60)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=int, default=5)
    minutes = parser.parse_args().minutes

    rates = BcrpExchangeRateProvider()
    five_years_ago = date.today() - timedelta(days=365 * 5)
    check(
        "Histórico 5 años (Yahoo, KC=F)",
        lambda: f"{len(YahooQuotationSource().fetch_daily_history(five_years_ago))} días",
    )
    check("Tipo de cambio actual (BCRP)", rates.fetch_latest)

    settings = get_settings()
    if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        from advisor.infrastructure.llm.anthropic_language_model import AnthropicLanguageModel

        model = AnthropicLanguageModel(settings.anthropic_api_key, settings.llm_model)
        check("LLM: elegir herramienta", lambda: model.choose_tool("¿Vendo ahora o espero?"))
    else:
        print("[OMITIDO] LLM: LLM_PROVIDER no es 'anthropic' (se usa el modelo por palabras clave)")

    compare_sources(minutes)


if __name__ == "__main__":
    main()
