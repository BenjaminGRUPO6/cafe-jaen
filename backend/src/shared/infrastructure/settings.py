"""Configuración leída de variables de entorno (archivo .env en desarrollo)."""

from decimal import Decimal
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Base de datos: SQLite en local (un archivo, sin instalar nada); PostgreSQL en producción
    database_url: str = "sqlite:///./cafe_jaen.db"

    # Seguridad (el secreto real nunca se versiona)
    jwt_secret: str = "change-me-in-production"
    session_days: int = 30
    consent_version: str = "2026-10"
    # Código de verificación del registro: primero por WhatsApp al celular (WhatsApp Business,
    # Meta Cloud API, con una plantilla de autenticación aprobada) ...
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_template: str = "codigo_verificacion"
    whatsapp_template_language: str = "es"
    # ... y si no, al correo. En Render (plan gratis bloquea SMTP) se usa Brevo:
    # BREVO_API_KEY y EMAIL_SENDER (un correo verificado en Brevo, puede ser de Gmail).
    # En local también sirve Gmail por SMTP con una «contraseña de aplicación».
    # Sin ninguno, el código solo lo ve el equipo en «Participantes».
    brevo_api_key: str = ""
    email_sender: str = ""
    email_sender_name: str = "Café Jaén"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    # WhatsApp del equipo (9 dígitos): si el código no llega, el caficultor lo pide desde la app
    team_whatsapp: str = ""

    # Mercado: precio mundial en vivo (HU02, HU03)
    local_price_factor: Decimal = Decimal("1")  # ajuste por diferencial y rendimiento local
    quotation_sources: list[str] = ["yahoo", "cnbc", "tradingview"]  # webs reales
    stooq_timezone: str = "Europe/Warsaw"
    stooq_api_key: str = ""  # Stooq exige clave desde 2026; sin ella se omite
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
    # Demostración: carga al arrancar precios SINTÉTICOS de cooperativas («Cooperativa JAENPERU
    # sintético A…F») si no hay ninguno. La bolsa y el tipo de cambio siguen siendo reales.
    demo_cooperatives: bool = False
    # Webs del dólar en vivo (USD/PEN), cada minuto; si ninguna responde se usa el BCRP del día
    exchange_rate_sources: list[str] = ["yahoo", "tradingview"]
    # Cuenta del equipo creada al arrancar (Render no tiene terminal en el plan gratuito)
    admin_phone: str = ""
    admin_password: str = ""
    # Carpeta del front-end compilado. Vacía en local (lo sirve Vite); en Render, /app/static
    static_dir: str = ""

    @field_validator("database_url")
    @classmethod
    def _postgres_driver(cls, value: str) -> str:
        """Neon y otros proveedores entregan «postgres://» o «postgresql://»: se usa psycopg2."""
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg2://" + value.removeprefix(prefix)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
