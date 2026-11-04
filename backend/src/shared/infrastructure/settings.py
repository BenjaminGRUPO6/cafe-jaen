"""Configuración leída de variables de entorno (archivo .env en desarrollo)."""

from decimal import Decimal
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Base de datos: SQLite en local (un archivo, sin instalar nada); PostgreSQL en producción
    database_url: str = "sqlite:///./cafe_jaen.db"

    # Seguridad (el secreto real nunca se versiona)
    jwt_secret: str = "change-me-in-production"
    session_days: int = 30
    consent_version: str = "2026-10"

    # Mercado: precio mundial en vivo (HU02, HU03)
    local_price_factor: Decimal = Decimal("1")  # ajuste por diferencial y rendimiento local
    quotation_sources: list[str] = ["yahoo", "stooq"]  # webs consultadas (ver el spike T01)
    stooq_timezone: str = "Europe/Warsaw"
    source_max_deviation: Decimal = Decimal("0.01")  # fuente a más de 1 % de la mediana: fuera
    max_quote_change: Decimal = Decimal("0.10")  # salto máximo aceptado entre cotizaciones
    market_opens: str = "04:15"  # hora de Nueva York (ICE, café arábica)
    market_closes: str = "13:30"
    stale_after_minutes: int = 20  # con la bolsa abierta, un precio más antiguo se marca
    stream_poll_seconds: float = 5.0
    stream_max_events: int | None = None  # solo para pruebas: cierra el flujo tras N eventos

    # Recomendación de venta (HU05)
    selling_threshold: Decimal = Decimal("0.03")  # 3 %
    selling_hit_rate_pct: float | None = None  # acierto de la prueba retrospectiva (T30)

    # Pronóstico
    forecast_horizon_days: int = 7
    forecast_history_days: int = 1825  # 5 años

    # Asesor: "keyword" funciona sin internet; "anthropic" usa el LLM real
    llm_provider: str = "keyword"
    anthropic_api_key: str = ""
    llm_model: str = "claude-haiku-5-5"

    # Planificador
    scheduler_enabled: bool = True
    daily_cycle_time: str = "14:05"  # hora de Lima, después del cierre de la bolsa
    timezone: str = "America/Lima"

    # API
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
