import logging
from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from orchestration.application.run_daily_cycle import CollectLivePrices, RunDailyCycle

logger = logging.getLogger(__name__)


def start_scheduler(
    live: CollectLivePrices,
    daily: RunDailyCycle,
    timezone: str,
    daily_cycle_time: str = "14:05",
    ensure_demo_data: Callable[[], bool] | None = None,
) -> BackgroundScheduler:
    """Programa a los agentes (hora de Lima, de lunes a viernes).

    - Cada minuto: recolección del precio en vivo (el Recolector no consulta con la bolsa cerrada).
    - Después del cierre: cierre del día, histórico y pronóstico.
    - Demostración (opcional): cada 5 minutos intenta cargar los precios sintéticos de
      cooperativas hasta que haya precio real de la bolsa; luego deja de intentarlo.
    """
    hour, minute = daily_cycle_time.split(":")
    scheduler = BackgroundScheduler(timezone=timezone)
    scheduler.add_job(
        _collect_safely,
        CronTrigger(day_of_week="mon-fri", minute="*", timezone=timezone),
        args=[live],
        id="live_prices",
        replace_existing=True,
        max_instances=1,  # si una consulta tarda, no se acumulan ejecuciones
        coalesce=True,
    )
    scheduler.add_job(
        _run_daily_safely,
        CronTrigger(day_of_week="mon-fri", hour=int(hour), minute=int(minute), timezone=timezone),
        args=[daily],
        id="daily_cycle",
        replace_existing=True,
    )
    if ensure_demo_data is not None:
        scheduler.add_job(
            _ensure_demo_safely,
            "interval",
            minutes=5,
            args=[scheduler, ensure_demo_data],
            id="demo_cooperatives",
            replace_existing=True,
            max_instances=1,
        )
    scheduler.start()
    return scheduler


def _ensure_demo_safely(scheduler: BackgroundScheduler, ensure: Callable[[], bool]) -> None:
    if ensure():
        logger.info("Precios sintéticos de cooperativas listos para la demostración")
        scheduler.remove_job("demo_cooperatives")


def _collect_safely(live: CollectLivePrices) -> None:
    report = live.execute()
    if report.get("issues"):
        logger.info("Recolección en vivo: %s", report)


def _run_daily_safely(daily: RunDailyCycle) -> None:
    report = daily.execute()
    logger.info(
        "Ciclo diario: recolección=%s, pronóstico=%s", report.collection, report.forecast_generated
    )
