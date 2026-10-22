from datetime import date, datetime

import pytest

from market.application.agents.analyst_agent import AnalystAgent
from market.application.agents.collector_agent import CollectorAgent
from market.application.collect_prices import CollectPrices
from market.application.get_live_price import GetLivePrice
from market.application.get_price_history import GetPriceHistory
from market.application.record_local_price import RecordLocalPrice
from market.domain.consensus import Consensus
from market.domain.market_hours import MarketHours
from market.domain.price_validator import PriceValidator
from market.domain.quintal_price import PriceConverter
from shared.domain.agent_message import AgentMessage
from tests.fakes import LIMA, FakeProvider, FixedClock, InMemoryPriceRepository, live, rate, source

CLOCK = FixedClock()
AT = datetime(2026, 11, 4, 8, 55, tzinfo=LIMA)


@pytest.fixture
def analyst() -> AnalystAgent:
    repo = InMemoryPriceRepository()
    repo.add_exchange_rate(rate("3.75", date(2026, 11, 4)))
    repo.add_live_quote(live("300", AT))
    return build_analyst(repo)


def build_analyst(repo: InMemoryPriceRepository) -> AnalystAgent:
    live_price = GetLivePrice(repo, PriceConverter(), MarketHours(), CLOCK)
    return AnalystAgent(
        live_price,
        GetPriceHistory(repo, PriceConverter(), CLOCK),
        RecordLocalPrice(repo, live_price, CLOCK),
        CLOCK,
    )


def ask(agent: AnalystAgent, action: str, content: dict[str, object] | None = None) -> AgentMessage:
    return agent.handle(AgentMessage.request("api", "analyst", action, content or {}, CLOCK.now()))


def test_answers_live_price_in_lima_time(analyst: AnalystAgent) -> None:
    reply = ask(analyst, "get_live_price")

    assert reply.content["price_soles"] == 1140.89
    assert reply.content["cents_per_pound"] == 300
    assert reply.content["quoted_at"] == "2026-11-04T08:55:00-05:00"
    assert reply.content["market_open"] is True


def test_answers_today_and_daily_history(analyst: AnalystAgent) -> None:
    today = ask(analyst, "get_price_history", {"period": "today"}).content
    daily = ask(analyst, "get_price_history", {"period": "30"}).content

    assert today["period"] == "today" and len(today["points"]) == 1
    assert daily["period"] == "30" and daily["points"] == []


def test_unknown_action_returns_failure(analyst: AnalystAgent) -> None:
    reply = ask(analyst, "bailar")

    assert reply.is_failure and "no soportada" in reply.content["reason"]


def test_missing_data_returns_failure() -> None:
    agent = build_analyst(InMemoryPriceRepository())

    assert ask(agent, "get_live_price").is_failure


def test_collector_agent_reports_collection() -> None:
    collect = CollectPrices(
        [source("Yahoo", live("300", AT))],
        FakeProvider(rate("3.75", date(2026, 11, 4))),
        InMemoryPriceRepository(),
        Consensus(),
        PriceValidator(),
        MarketHours(),
        CLOCK,
    )
    agent = CollectorAgent(collect, CLOCK)

    reply = agent.handle(
        AgentMessage.request("scheduler", "collector", "collect_prices", {}, CLOCK.now())
    )

    assert reply.content["quotation_saved"] and reply.content["sources_ok"] == ["Yahoo"]
    assert agent.handle(AgentMessage.request("x", "collector", "otra", {}, CLOCK.now())).is_failure


def test_records_local_price_and_includes_estimate_in_live_price(analyst: AnalystAgent) -> None:
    # HU12: S/ 900 pagados con la bolsa a S/ 1140,89 → 78,9 %
    content = {"cooperative": "Coop. A", "coffee_type": "convencional", "paid_soles": 900}

    recorded = ask(analyst, "record_local_price", content).content
    estimate = ask(analyst, "get_live_price").content["local_estimates"][0]
    listed = ask(analyst, "get_local_prices").content["observations"]

    assert recorded["ratio_pct"] == 78.9 and recorded["exchange_soles"] == 1140.89
    assert estimate["coffee_type"] == "convencional" and estimate["estimated_soles"] == 900.0
    assert estimate["observations"] == 1 and estimate["few_data"] is True
    assert listed[0]["cooperative"] == "Coop. A"


def test_invalid_local_price_returns_failure(analyst: AnalystAgent) -> None:
    content = {"cooperative": "Coop. A", "coffee_type": "convencional", "paid_soles": 90}

    reply = ask(analyst, "record_local_price", content)

    assert reply.is_failure and "revisa si está bien escrito" in reply.content["reason"]
