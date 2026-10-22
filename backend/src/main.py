"""Raíz de composición: el único lugar donde se crean los adaptadores concretos
y se inyectan en los casos de uso y agentes (inyección de dependencias manual).

Ejecutar en desarrollo:  uvicorn main:app --reload --app-dir src
"""

import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from decimal import Decimal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from advisor.application.agents.advisor_agent import AdvisorAgent
from advisor.application.answer_question import AnswerQuestion
from advisor.domain.ports.language_model import LanguageModel
from advisor.infrastructure.api.advisor_router import build_advisor_router
from advisor.infrastructure.llm.anthropic_language_model import AnthropicLanguageModel
from advisor.infrastructure.llm.keyword_language_model import KeywordLanguageModel
from decision.application.agents.strategist_agent import StrategistAgent
from decision.application.get_selling_advice import GetSellingAdvice
from decision.domain.selling_decision import SellingDecision
from decision.infrastructure.api.decision_router import build_decision_router
from forecasting.application.agents.forecaster_agent import ForecasterAgent
from forecasting.application.generate_forecast import GenerateForecast
from forecasting.application.get_forecast import GetForecast
from forecasting.infrastructure.api.forecast_router import build_forecast_router
from forecasting.infrastructure.models.elm_forecast_model import ElmForecastModel
from forecasting.infrastructure.models.naive_forecast_model import NaiveDriftForecastModel
from forecasting.infrastructure.persistence.sqlalchemy_forecast_repository import (
    SqlAlchemyForecastRepository,
)
from identity.application.authenticate_user import AuthenticateUser
from identity.application.register_user import RegisterUser
from identity.infrastructure.api.auth_router import build_auth_router
from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
    SqlAlchemyUserRepository,
)
from identity.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from identity.infrastructure.security.jwt_token_service import JwtTokenService
from market.application.agents.analyst_agent import AnalystAgent
from market.application.agents.collector_agent import CollectorAgent
from market.application.collect_prices import CollectPrices
from market.application.get_live_price import GetLivePrice
from market.application.get_price_history import GetPriceHistory
from market.application.record_local_price import RecordLocalPrice
from market.domain.consensus import Consensus
from market.domain.market_hours import MarketHours
from market.domain.ports.sources import ExchangeRateProvider, QuotationSource
from market.domain.price_validator import PriceValidator
from market.domain.quintal_price import PriceConverter
from market.infrastructure.api.market_router import build_market_router
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from market.infrastructure.sources.bcrp_exchange_rate_provider import BcrpExchangeRateProvider
from market.infrastructure.sources.demo_quotation_source import DemoQuotationSource
from market.infrastructure.sources.stooq_quotation_source import StooqQuotationSource
from market.infrastructure.sources.yahoo_quotation_source import YahooQuotationSource
from orchestration.application.dispatch_request import DispatchRequest
from orchestration.application.run_daily_cycle import CollectLivePrices, RunDailyCycle
from orchestration.infrastructure.langgraph.langgraph_agent_router import LangGraphAgentRouter
from orchestration.infrastructure.persistence.sqlalchemy_trace_repository import (
    SqlAlchemyTraceRepository,
)
from orchestration.infrastructure.scheduler.daily_cycle_scheduler import start_scheduler
from shared.domain.ports.clock import Clock
from shared.infrastructure.api.dependencies import build_require_admin, build_require_user
from shared.infrastructure.database import create_db_engine, create_session_factory
from shared.infrastructure.settings import Settings, get_settings
from shared.infrastructure.system_clock import SystemClock

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
# El planificador corre cada minuto: solo se registran sus advertencias y errores
logging.getLogger("apscheduler").setLevel(logging.WARNING)


@dataclass
class Overrides:
    """Permite reemplazar adaptadores externos (pruebas y desarrollo sin internet)."""

    quotation_sources: Sequence[QuotationSource] | None = None
    exchange_rate_provider: ExchangeRateProvider | None = None
    language_model: LanguageModel | None = None
    clock: Clock | None = None


def create_app(settings: Settings | None = None, overrides: Overrides | None = None) -> FastAPI:
    settings = settings or get_settings()
    overrides = overrides or Overrides()
    clock = overrides.clock or SystemClock(settings.timezone)
    engine = create_db_engine(settings.database_url)
    sessions = create_session_factory(engine)

    # ---------- identity
    users = SqlAlchemyUserRepository(sessions)
    hasher = BcryptPasswordHasher()
    tokens = JwtTokenService(settings.jwt_secret, settings.session_days, clock)
    register = RegisterUser(
        users, SqlAlchemyInvitationCodeRepository(sessions), hasher, clock, settings.consent_version
    )
    authenticate = AuthenticateUser(users, hasher, tokens)

    # ---------- market (Recolector y Analista): precio mundial en vivo
    prices = SqlAlchemyPriceRepository(sessions)
    converter = PriceConverter(settings.local_price_factor)
    market_hours = MarketHours(_time(settings.market_opens), _time(settings.market_closes))
    collector = CollectorAgent(
        CollectPrices(
            overrides.quotation_sources or _quotation_sources(settings, prices),
            overrides.exchange_rate_provider or BcrpExchangeRateProvider(),
            prices,
            Consensus(settings.source_max_deviation),
            PriceValidator(settings.max_quote_change),
            market_hours,
            clock,
        ),
        clock,
    )
    get_live_price = GetLivePrice(
        prices, converter, market_hours, clock, timedelta(minutes=settings.stale_after_minutes)
    )
    analyst = AnalystAgent(
        get_live_price,
        GetPriceHistory(prices, converter, clock),
        RecordLocalPrice(prices, get_live_price, clock),
        clock,
    )

    # ---------- forecasting (Predictor)
    forecasts = SqlAlchemyForecastRepository(sessions)
    models = [ElmForecastModel(), NaiveDriftForecastModel()]
    forecaster = ForecasterAgent(
        GenerateForecast(models, forecasts, clock, horizon=settings.forecast_horizon_days),
        GetForecast(forecasts),
        clock,
    )

    # ---------- orchestration (Supervisor) + advisor (Asesor)
    router = LangGraphAgentRouter(clock)
    supervisor = DispatchRequest(router, SqlAlchemyTraceRepository(sessions), clock)
    language_model = overrides.language_model or _language_model(settings)
    advisor = AdvisorAgent(AnswerQuestion(language_model, supervisor), clock)
    # ---------- decision (Estratega de venta)
    strategist = StrategistAgent(
        GetSellingAdvice(supervisor, SellingDecision(settings.selling_threshold), clock),
        clock,
        settings.selling_hit_rate_pct,
    )
    # Los agentes se registran al final: asesor y estratega necesitan al supervisor ya creado
    router.register([collector, analyst, forecaster, strategist, advisor])
    live_collection = CollectLivePrices(supervisor)
    daily_cycle = RunDailyCycle(supervisor, settings.forecast_history_days)

    def latest_quote_time() -> datetime | None:
        quote = prices.last_live_quote()
        return quote.quoted_at if quote else None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        scheduler = (
            start_scheduler(
                live_collection, daily_cycle, settings.timezone, settings.daily_cycle_time
            )
            if settings.scheduler_enabled
            else None
        )
        yield
        if scheduler:
            scheduler.shutdown(wait=False)
        engine.dispose()

    app = FastAPI(title="Café Jaén API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.daily_cycle = daily_cycle  # usados por el script de ejecución manual
    app.state.live_collection = live_collection

    require_user = build_require_user(tokens)
    app.include_router(build_auth_router(register, authenticate, tokens), prefix="/api")
    app.include_router(
        build_market_router(
            supervisor,
            require_user,
            build_require_admin(tokens),
            latest_quote_time,
            settings.stream_poll_seconds,
            settings.stream_max_events,
        ),
        prefix="/api",
    )
    app.include_router(build_forecast_router(supervisor, require_user), prefix="/api")
    app.include_router(build_decision_router(supervisor, require_user), prefix="/api")
    app.include_router(build_advisor_router(supervisor, require_user), prefix="/api")

    @app.get("/api/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _quotation_sources(
    settings: Settings, prices: SqlAlchemyPriceRepository
) -> list[QuotationSource]:
    """Crea un adaptador por cada web configurada (agregar una web = agregar un adaptador)."""

    def last_known() -> Decimal | None:
        quote = prices.last_live_quote()
        closes = prices.last_quotations(limit=1)
        return quote.cents_per_pound if quote else (closes[0].cents_per_pound if closes else None)

    available: dict[str, QuotationSource] = {
        "yahoo": YahooQuotationSource(),
        "stooq": StooqQuotationSource(timezone=settings.stooq_timezone),
        "demo": DemoQuotationSource(last_known),  # solo desarrollo sin internet
    }
    return [available[name] for name in settings.quotation_sources]


def _time(text: str) -> time:
    hour, minute = text.split(":")
    return time(int(hour), int(minute))


def _language_model(settings: Settings) -> LanguageModel:
    if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicLanguageModel(settings.anthropic_api_key, settings.llm_model)
    return KeywordLanguageModel()


app = create_app()
