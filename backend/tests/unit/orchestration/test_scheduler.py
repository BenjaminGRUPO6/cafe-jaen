"""PA-02-1 (HU02) y HU06: el planificador dispara a los agentes sin intervención humana."""

from orchestration.application.run_daily_cycle import CollectLivePrices, RunDailyCycle
from orchestration.infrastructure.scheduler.daily_cycle_scheduler import start_scheduler
from tests.fakes import FakeGateway


def test_live_collection_every_minute_and_daily_cycle_after_close() -> None:
    gateway = FakeGateway()
    scheduler = start_scheduler(
        CollectLivePrices(gateway), RunDailyCycle(gateway, 30), "America/Lima", "14:05"
    )
    try:
        live = {f.name: str(f) for f in scheduler.get_job("live_prices").trigger.fields}
        daily_trigger = scheduler.get_job("daily_cycle").trigger
        daily = {f.name: str(f) for f in daily_trigger.fields}
    finally:
        scheduler.shutdown(wait=False)

    assert live["day_of_week"] == "mon-fri" and live["minute"] == "*"
    assert daily["day_of_week"] == "mon-fri"
    assert (daily["hour"], daily["minute"]) == ("14", "5")
    assert str(daily_trigger.timezone) == "America/Lima"
