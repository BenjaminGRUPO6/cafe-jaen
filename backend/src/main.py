"""Raíz de composición: el único lugar donde se crean los adaptadores concretos
y se inyectan en los casos de uso y agentes (inyección de dependencias manual).

Ejecutar en desarrollo:  uvicorn main:app --reload --app-dir src
"""

import logging
import secrets
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, time, timedelta

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
from identity.application.delete_participant import DeleteParticipant
from identity.application.email_verification import SendVerificationCode, VerifyAccount
from identity.application.list_participants import ListParticipants
from identity.application.manage_invitation_codes import ManageInvitationCodes
from identity.application.register_user import RegisterUser
from identity.domain.ports.email_sender import EmailSender
from identity.infrastructure.api.admin_router import build_participants_router
from identity.infrastructure.api.auth_router import build_auth_router
from identity.infrastructure.email.senders import build_email_sender
from identity.infrastructure.persistence.sqlalchemy_repositories import (
    SqlAlchemyInvitationCodeRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyVerificationRepository,
)
from identity.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from identity.infrastructure.security.jwt_token_service import JwtTokenService
from market.application.agents.analyst_agent import AnalystAgent
from market.application.agents.collector_agent import CollectorAgent
from market.application.collect_prices import CollectPrices
from market.application.correct_local_price import CorrectLocalPrice
from market.application.get_live_price import GetLivePrice
from market.application.get_price_history import GetPriceHistory
from market.application.get_price_log import GetPriceLog
from market.application.manage_cooperatives import ManageCooperatives
from market.application.manage_synthetic_data import ManageSyntheticData
from market.application.record_local_price import RecordLocalPrice
from market.domain.consensus import Consensus
from market.domain.local_price import LocalPriceEstimator
from market.domain.market_hours import MarketHours
from market.domain.ports.sources import (
    ExchangeRateProvider,
    LiveExchangeRateSource,
    QuotationSource,
)
from market.domain.price_validator import PriceValidator
from market.domain.quintal_price import PriceConverter
from market.infrastructure.api.admin_market_router import build_admin_market_router
from market.infrastructure.api.market_router import build_market_router
from market.infrastructure.persistence.sqlalchemy_cooperative_repository import (
    SqlAlchemyCooperativeRepository,
)
from market.infrastructure.persistence.sqlalchemy_price_repository import SqlAlchemyPriceRepository
from market.infrastructure.sources.bcrp_exchange_rate_provider import BcrpExchangeRateProvider
from market.infrastructure.sources.live_exchange_rate_sources import build_exchange_sources
from market.infrastructure.sources.registry import build_sources
from orchestration.application.dispatch_request import DispatchRequest
from orchestration.application.run_daily_cycle import CollectLivePrices, RunDailyCycle
from orchestration.infrastructure.langgraph.langgraph_agent_router import LangGraphAgentRouter
from orchestration.infrastructure.persistence.sqlalchemy_trace_repository import (
    SqlAlchemyTraceRepository,
)
from orchestration.infrastructure.scheduler.daily_cycle_scheduler import start_scheduler
from shared.domain.ports.clock import Clock
from shared.infrastructure.api.dependencies import build_require_admin, build_require_user
from shared.infrastructure.api.spa import mount_single_page_app
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
    live_exchange_sources: Sequence[LiveExchangeRateSource] | None = None
    language_model: LanguageModel | None = None
    email_sender: EmailSender | None = None
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
    codes = SqlAlchemyInvitationCodeRepository(sessions)
    register = RegisterUser(users, codes, hasher, clock, settings.consent_version)
    verifications = SqlAlchemyVerificationRepository(sessions)
    email_sender = overrides.email_sender or build_email_sender(
        settings.brevo_api_key,
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_user,
        settings.smtp_password,
        settings.email_sender,
        settings.email_sender_name,
    )
    send_code = SendVerificationCode(users, verifications, email_sender, clock, secrets.choice)
    verify = VerifyAccount(users, verifications, tokens, clock)
    authenticate = AuthenticateUser(users, hasher, tokens, clock)

    # ---------- market (Recolector y Analista): precio mundial en vivo
    prices = SqlAlchemyPriceRepository(sessions)
    converter = PriceConverter(settings.local_price_factor)
    market_hours = MarketHours(_time(settings.market_opens), _time(settings.market_closes))
    collector = CollectorAgent(
        CollectPrices(
            overrides.quotation_sources
            or build_sources(settings.quotation_sources, settings.stooq_timezone),
            overrides.exchange_rate_provider or BcrpExchangeRateProvider(),
            prices,
            Consensus(settings.source_max_deviation),
            PriceValidator(settings.max_quote_change),
            market_hours,
            clock,
            overrides.live_exchange_sources
            if overrides.live_exchange_sources is not None
            else build_exchange_sources(settings.exchange_rate_sources),
        ),
        clock,
    )
    get_live_price = GetLivePrice(
        prices, converter, market_hours, clock, timedelta(minutes=settings.stale_after_minutes)
    )
    cooperatives = SqlAlchemyCooperativeRepository(sessions)
    analyst = AnalystAgent(
        get_live_price,
        GetPriceHistory(prices, converter, clock),
        RecordLocalPrice(prices, get_live_price, cooperatives, clock),
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
    synthetic_data = ManageSyntheticData(prices, cooperatives, converter, clock)

    def latest_quote_time() -> datetime | None:
        quote = prices.last_live_quote()
        return quote.quoted_at if quote else None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        scheduler = (
            start_scheduler(
                live_collection,
                daily_cycle,
                settings.timezone,
                settings.daily_cycle_time,
                synthetic_data.ensure_loaded if settings.demo_cooperatives else None,
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

    # Una cuenta eliminada por el equipo pierde la sesión aunque su token no haya vencido
    def is_active(user_id: str) -> bool:
        return users.get_by_id(user_id) is not None

    require_user = build_require_user(tokens, is_active)
    require_admin = build_require_admin(tokens, is_active)
    app.include_router(build_auth_router(register, authenticate, send_code, verify), prefix="/api")
    app.include_router(
        build_participants_router(
            ListParticipants(users, codes, verifications),
            ManageInvitationCodes(codes, secrets.choice),
            DeleteParticipant(users),
            require_admin,
        ),
        prefix="/api",
    )
    app.include_router(
        build_market_router(
            supervisor,
            require_user,
            require_admin,
            latest_quote_time,
            settings.stream_poll_seconds,
            settings.stream_max_events,
        ),
        prefix="/api",
    )
    app.include_router(
        build_admin_market_router(
            ManageCooperatives(cooperatives),
            CorrectLocalPrice(prices),
            GetPriceLog(prices, converter, LocalPriceEstimator(), clock),
            synthetic_data,
            require_user,
            require_admin,
        ),
        prefix="/api",
    )
    app.include_router(build_forecast_router(supervisor, require_user), prefix="/api")
    app.include_router(build_decision_router(supervisor, require_user), prefix="/api")
    app.include_router(build_advisor_router(supervisor, require_user), prefix="/api")

    @app.get("/api/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Despliegue en un solo servicio: la API también entrega la app (va al final)
    if settings.static_dir:
        mount_single_page_app(app, settings.static_dir)

    return app


def _time(text: str) -> time:
    hour, minute = text.split(":")
    return time(int(hour), int(minute))


def _language_model(settings: Settings) -> LanguageModel:
    if settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicLanguageModel(settings.anthropic_api_key, settings.llm_model)
    return KeywordLanguageModel()


app = create_app()
