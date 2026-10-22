"""PA-06-1 y PA-06-2 (HU06): se elige el modelo de menor MAPE y se guarda el pronóstico."""

import pytest

from forecasting.application.agents.forecaster_agent import ForecasterAgent
from forecasting.application.generate_forecast import GenerateForecast
from forecasting.application.get_forecast import GetForecast
from forecasting.domain.errors import ForecastNotAvailableError, NotEnoughHistoryError
from shared.domain.agent_message import AgentMessage
from tests.fakes import ConstantModel, FixedClock, InMemoryForecastRepository

HISTORY = [1000.0] * 120


def test_selects_model_with_lowest_mape_and_saves_it() -> None:
    repository = InMemoryForecastRepository()
    use_case = GenerateForecast(
        [ConstantModel("malo", 1200), ConstantModel("bueno", 1010)], repository, FixedClock()
    )

    forecast = use_case.execute(HISTORY)

    assert forecast.model_name == "bueno"
    assert float(forecast.mape) == pytest.approx(1.0)
    assert len(forecast.points) == 7
    assert repository.latest() == forecast


def test_requires_enough_history() -> None:
    with pytest.raises(NotEnoughHistoryError):
        GenerateForecast(
            [ConstantModel("m", 1)], InMemoryForecastRepository(), FixedClock()
        ).execute([1.0] * 50)


def test_get_forecast_without_data_fails() -> None:
    with pytest.raises(ForecastNotAvailableError):
        GetForecast(InMemoryForecastRepository()).execute()


def test_agent_generates_from_history_and_answers_with_disclaimer() -> None:
    clock = FixedClock()
    repository = InMemoryForecastRepository()
    agent = ForecasterAgent(
        GenerateForecast([ConstantModel("base", 1000)], repository, clock),
        GetForecast(repository),
        clock,
    )
    points = [{"date": "2026-01-01", "price_soles": value} for value in HISTORY]

    generated = agent.handle(
        AgentMessage.request(
            "scheduler", "forecaster", "generate_forecast", {"points": points}, clock.now()
        )
    )
    latest = agent.handle(
        AgentMessage.request("api", "forecaster", "get_forecast", {}, clock.now())
    )

    assert not generated.is_failure
    assert latest.content["disclaimer"].startswith("Pronóstico referencial")
    assert latest.content["points"][0]["date"] == "2026-11-05"


def test_agent_reports_not_enough_history_as_failure() -> None:
    clock = FixedClock()
    repository = InMemoryForecastRepository()
    agent = ForecasterAgent(
        GenerateForecast([ConstantModel("m", 1)], repository, clock), GetForecast(repository), clock
    )

    reply = agent.handle(
        AgentMessage.request(
            "scheduler", "forecaster", "generate_forecast", {"points": []}, clock.now()
        )
    )

    assert reply.is_failure
