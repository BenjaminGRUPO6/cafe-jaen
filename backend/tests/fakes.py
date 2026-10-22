"""Dobles de prueba (fakes) de los puertos: permiten probar el núcleo sin BD ni internet."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from forecasting.domain.forecast import Forecast
from identity.domain.invitation_code import InvitationCode
from identity.domain.phone_number import PhoneNumber
from identity.domain.user import User
from market.domain.errors import SourceUnavailableError
from market.domain.local_price import LocalPriceObservation
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from orchestration.domain.trace import AgentTrace
from shared.domain.agent_message import AgentMessage

LIMA = ZoneInfo("America/Lima")


# ---------------------------------------------------------------- shared
@dataclass
class FixedClock:
    current: datetime = field(default_factory=lambda: datetime(2026, 11, 4, 9, 0, tzinfo=LIMA))

    def now(self) -> datetime:
        return self.current

    def today(self) -> date:
        return self.current.date()


class FakeGateway:
    """Responde con funciones predefinidas por (receptor, acción) y registra cada solicitud."""

    def __init__(self, clock: FixedClock | None = None) -> None:
        self.clock = clock or FixedClock()
        self.requests: list[AgentMessage] = []
        self._handlers: dict[tuple[str, str], Callable[[AgentMessage], AgentMessage]] = {}

    def answer(self, receiver: str, action: str, content: dict[str, Any]) -> None:
        self._handlers[(receiver, action)] = lambda msg: msg.reply_inform(content, self.clock.now())

    def fail(self, receiver: str, action: str, reason: str = "falla simulada") -> None:
        self._handlers[(receiver, action)] = lambda msg: msg.reply_failure(reason, self.clock.now())

    def request(
        self, sender: str, receiver: str, action: str, content: dict[str, Any] | None = None
    ) -> AgentMessage:
        message = AgentMessage.request(sender, receiver, action, content or {}, self.clock.now())
        self.requests.append(message)
        handler = self._handlers.get((receiver, action))
        return (
            handler(message)
            if handler
            else message.reply_failure("sin respuesta", self.clock.now())
        )


# ---------------------------------------------------------------- identity
class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.redeemed: list[InvitationCode] = []

    def get_by_phone(self, phone: PhoneNumber) -> User | None:
        return next((u for u in self.users.values() if u.phone == phone), None)

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        self.users[user.id] = user
        if redeemed_code:
            self.redeemed.append(redeemed_code)


class InMemoryInvitationCodeRepository:
    def __init__(self, *codes: InvitationCode) -> None:
        self.codes = {c.code: c for c in codes}

    def get(self, code: str) -> InvitationCode | None:
        return self.codes.get(code)


class FakePasswordHasher:
    """Hash reversible solo para pruebas (el real es bcrypt)."""

    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokenIssuer:
    def issue(self, user_id: str, role: str = "farmer") -> str:
        return f"token-{user_id}-{role}"


# ---------------------------------------------------------------- market
class InMemoryPriceRepository:
    def __init__(self) -> None:
        self.live: list[LiveQuote] = []
        self.quotations: list[Quotation] = []
        self.rates: dict[date, ExchangeRate] = {}
        self.local: list[LocalPriceObservation] = []

    def add_local_observation(self, observation: LocalPriceObservation) -> None:
        self.local.append(observation)

    def local_observations_since(self, moment: datetime) -> list[LocalPriceObservation]:
        recent = [o for o in self.local if o.observed_at >= moment]
        return sorted(recent, key=lambda o: o.observed_at, reverse=True)

    def add_live_quote(self, quote: LiveQuote) -> None:
        self.live.append(quote)

    def last_live_quote(self) -> LiveQuote | None:
        return max(self.live, key=lambda q: q.quoted_at) if self.live else None

    def live_quotes_between(self, start: datetime, end: datetime) -> list[LiveQuote]:
        return sorted(
            (q for q in self.live if start <= q.quoted_at < end), key=lambda q: q.quoted_at
        )

    def save_daily_close(self, quotation: Quotation) -> None:
        self.quotations = [q for q in self.quotations if q.quoted_on != quotation.quoted_on]
        self.quotations.append(quotation)

    def last_quotations(self, limit: int) -> list[Quotation]:
        return sorted(self.quotations, key=lambda q: q.quoted_on, reverse=True)[:limit]

    def quotations_since(self, day: date) -> list[Quotation]:
        return sorted((q for q in self.quotations if q.quoted_on >= day), key=lambda q: q.quoted_on)

    def add_exchange_rate(self, rate: ExchangeRate) -> None:
        self.rates[rate.rated_on] = rate

    def exchange_rate_on(self, day: date) -> ExchangeRate | None:
        candidates = [r for d, r in self.rates.items() if d <= day]
        return max(candidates, key=lambda r: r.rated_on) if candidates else None

    def exchange_rates_since(self, day: date) -> list[ExchangeRate]:
        return sorted(
            (r for r in self.rates.values() if r.rated_on >= day), key=lambda r: r.rated_on
        )


class FakeProvider:
    """Devuelve los valores en orden; un SourceUnavailableError en la lista simula una caída."""

    def __init__(self, *results: Any, name: str = "Fuente") -> None:
        self._results = list(results)
        self.name = name
        self.calls = 0

    def fetch_latest(self) -> Any:
        self.calls += 1
        result = self._results.pop(0) if len(self._results) > 1 else self._results[0]
        if isinstance(result, SourceUnavailableError):
            raise result
        return result


def live(cents: str, at: datetime, source: str = "Yahoo Finance") -> LiveQuote:
    return LiveQuote(Decimal(cents), at, (source,))


def source(name: str, *results: Any) -> FakeProvider:
    """Fuente web simulada que devuelve cotizaciones con su propio nombre."""
    return FakeProvider(
        *[
            live(str(r.cents_per_pound), r.quoted_at, name) if isinstance(r, LiveQuote) else r
            for r in results
        ],
        name=name,
    )


def quotation(cents: str, day: date, source: str = "Yahoo Finance") -> Quotation:
    return Quotation(Decimal(cents), day, source)


def rate(value: str, day: date) -> ExchangeRate:
    return ExchangeRate(Decimal(value), day, "BCRP")


def business_days(end: date, count: int) -> list[date]:
    """Los últimos `count` días hábiles hasta `end` (inclusive), en orden."""
    days: list[date] = []
    current = end
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current)
        current -= timedelta(days=1)
    return sorted(days)


# ---------------------------------------------------------------- forecasting
class InMemoryForecastRepository:
    def __init__(self) -> None:
        self.saved: list[Forecast] = []

    def save(self, forecast: Forecast) -> None:
        self.saved.append(forecast)

    def latest(self) -> Forecast | None:
        return self.saved[-1] if self.saved else None


class ConstantModel:
    """Modelo de prueba que siempre predice el mismo valor."""

    def __init__(self, name: str, value: float) -> None:
        self.name = name
        self._value = value

    def predict(self, history: Any, horizon: int) -> list[float]:
        return [self._value] * horizon


# ---------------------------------------------------------------- orchestration
class InMemoryTraceRepository:
    def __init__(self) -> None:
        self.traces: list[AgentTrace] = []

    def add(self, trace: AgentTrace) -> None:
        self.traces.append(trace)
