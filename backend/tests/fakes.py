"""Dobles de prueba (fakes) de los puertos: permiten probar el núcleo sin BD ni internet."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from forecasting.domain.forecast import Forecast
from identity.domain.email_address import EmailAddress
from identity.domain.invitation_code import InvitationCode
from identity.domain.participant import CodeSummary, Participant
from identity.domain.phone_number import PhoneNumber
from identity.domain.ports.email_sender import EmailNotSentError
from identity.domain.user import Role, User
from identity.domain.verification import EmailVerification
from market.domain.cooperative import Cooperative
from market.domain.errors import SourceUnavailableError
from market.domain.local_price import LocalPriceObservation
from market.domain.quotation import ExchangeRate, LiveQuote, Quotation
from market.domain.source_reading import PriceCollection
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
        self.logins: dict[str, datetime] = {}

    def get_by_phone(self, phone: PhoneNumber) -> User | None:
        return next((u for u in self.users.values() if u.phone == phone), None)

    def get_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: EmailAddress) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    def add(self, user: User, redeemed_code: InvitationCode | None) -> None:
        self.users[user.id] = user
        if redeemed_code:
            self.redeemed.append(redeemed_code)

    def mark_verified(self, user_id: str, at: datetime) -> None:
        self.users[user_id] = replace(self.users[user_id], verified_at=at)

    def record_login(self, user_id: str, at: datetime) -> None:
        self.logins[user_id] = at

    def delete(self, user_id: str) -> None:
        self.users.pop(user_id, None)
        self.redeemed = [c for c in self.redeemed if c.used_by != user_id]

    def count_admins(self) -> int:
        return sum(1 for u in self.users.values() if u.role is Role.ADMIN)

    def participants(self) -> list[Participant]:
        codes = {c.used_by: c.code for c in self.redeemed}
        return [
            Participant(
                u.id,
                u.phone.value,
                u.role,
                u.created_at,
                codes.get(u.id),
                self.logins.get(u.id),
                u.email.value if u.email else None,
                u.is_verified,
            )
            for u in sorted(self.users.values(), key=lambda u: u.created_at, reverse=True)
        ]


class InMemoryVerificationRepository:
    def __init__(self) -> None:
        self.items: dict[str, EmailVerification] = {}

    def save(self, verification: EmailVerification) -> None:
        self.items[verification.user_id] = verification

    def get(self, user_id: str) -> EmailVerification | None:
        return self.items.get(user_id)

    def delete(self, user_id: str) -> None:
        self.items.pop(user_id, None)

    def pending(self) -> dict[str, EmailVerification]:
        return dict(self.items)


class FakeEmailSender:
    """Guarda los correos en vez de enviarlos; `fail=True` simula un proveedor caído."""

    def __init__(self, fail: bool = False) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self.fail = fail

    def send(self, to: str, subject: str, text: str) -> None:
        if self.fail:
            raise EmailNotSentError("caído")
        self.sent.append((to, subject, text))

    def last_code(self) -> str:
        """El código de 6 dígitos del último correo enviado."""
        return next(w for w in self.sent[-1][2].split() if w.isdigit() and len(w) == 6)


class InMemoryInvitationCodeRepository:
    def __init__(self, *codes: InvitationCode) -> None:
        self.codes = {c.code: c for c in codes}

    def get(self, code: str) -> InvitationCode | None:
        return self.codes.get(code)

    def summary(self) -> CodeSummary:
        return CodeSummary(len(self.codes), sum(c.is_used for c in self.codes.values()))

    def all(self) -> list[InvitationCode]:
        return sorted(self.codes.values(), key=lambda c: (c.is_used, c.code))

    def add_many(self, codes: list[str], role: Role = Role.FARMER) -> None:
        for code in codes:
            self.codes[code] = InvitationCode(code, role=role)


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
class InMemoryCooperativeRepository:
    def __init__(self, *names: str) -> None:
        self.items: dict[int, Cooperative] = {}
        self.renamed: list[tuple[str, str]] = []
        self.with_prices: set[str] = set()
        for name in names:
            self.add(Cooperative.create(name, "Jaén", None))

    def all(self) -> list[Cooperative]:
        return sorted(self.items.values(), key=lambda c: (not c.active, c.name))

    def get(self, cooperative_id: int) -> Cooperative | None:
        return self.items.get(cooperative_id)

    def get_by_name(self, name: str) -> Cooperative | None:
        wanted = name.strip().lower()
        return next((c for c in self.items.values() if c.name.lower() == wanted), None)

    def add(self, cooperative: Cooperative) -> Cooperative:
        saved = replace(cooperative, id=len(self.items) + 1)
        self.items[saved.id] = saved  # type: ignore[index]
        return saved

    def update(self, cooperative: Cooperative, previous_name: str) -> None:
        self.items[cooperative.id] = cooperative  # type: ignore[index]
        if cooperative.name != previous_name:
            self.renamed.append((previous_name, cooperative.name))

    def delete(self, cooperative_id: int) -> None:
        del self.items[cooperative_id]

    def has_prices(self, name: str) -> bool:
        return name in self.with_prices


class InMemoryPriceRepository:
    def __init__(self) -> None:
        self.live: list[LiveQuote] = []
        self.quotations: list[Quotation] = []
        self.rates: dict[date, ExchangeRate] = {}
        self.local: list[LocalPriceObservation] = []
        self.collections: list[PriceCollection] = []
        self.live_rates: list[ExchangeRate] = []

    def add_live_exchange_rate(self, rate: ExchangeRate) -> None:
        self.live_rates.append(rate)

    def last_live_exchange_rate(self) -> ExchangeRate | None:
        return max(self.live_rates, key=lambda r: r.rated_at or 0) if self.live_rates else None  # type: ignore[arg-type,return-value]

    def live_exchange_rates_between(self, start: datetime, end: datetime) -> list[ExchangeRate]:
        found = [r for r in self.live_rates if r.rated_at and start <= r.rated_at < end]
        return sorted(found, key=lambda r: r.rated_at)  # type: ignore[arg-type,return-value]

    def add_collection(self, collection: PriceCollection) -> None:
        self.collections.append(collection)

    def collections_between(self, start: datetime, end: datetime) -> list[PriceCollection]:
        return sorted(
            (c for c in self.collections if start <= c.collected_at < end),
            key=lambda c: c.collected_at,
        )

    def add_local_observation(self, observation: LocalPriceObservation) -> LocalPriceObservation:
        saved = replace(observation, id=len(self.local) + 1)
        self.local.append(saved)
        return saved

    def get_local_observation(self, observation_id: int) -> LocalPriceObservation | None:
        return next((o for o in self.local if o.id == observation_id), None)

    def update_local_paid(self, observation_id: int, paid_soles: Decimal) -> None:
        self.local = [
            replace(o, paid_soles=paid_soles) if o.id == observation_id else o for o in self.local
        ]

    def delete_local_observation(self, observation_id: int) -> None:
        self.local = [o for o in self.local if o.id != observation_id]

    def add_local_observations(self, observations: Sequence[LocalPriceObservation]) -> None:
        for observation in observations:
            self.add_local_observation(observation)

    def count_local_observations_of(self, cooperatives: Sequence[str]) -> int:
        return sum(1 for o in self.local if o.cooperative in cooperatives)

    def delete_local_observations_of(self, cooperatives: Sequence[str]) -> int:
        before = len(self.local)
        self.local = [o for o in self.local if o.cooperative not in cooperatives]
        return before - len(self.local)

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
