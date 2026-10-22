from datetime import tzinfo
from decimal import Decimal
from typing import Any

from market.application.get_live_price import GetLivePrice
from market.application.get_price_history import GetPriceHistory
from market.application.record_local_price import RecordLocalPrice, RecordLocalPriceCommand
from market.domain.errors import MarketError
from market.domain.live_price import HistoryPoint, IntradayPoint, LivePrice
from market.domain.local_price import LocalEstimate, LocalPriceObservation
from shared.domain.agent_message import AgentMessage
from shared.domain.contract import Action, AgentName
from shared.domain.ports.clock import Clock

DEFAULT_HISTORY_DAYS = 30
TODAY = "today"


class AnalystAgent:
    """Agente Analista: traduce la cotización a soles por quintal (en vivo e histórico)."""

    name = AgentName.ANALYST

    def __init__(
        self,
        get_live_price: GetLivePrice,
        get_price_history: GetPriceHistory,
        record_local_price: RecordLocalPrice,
        clock: Clock,
    ) -> None:
        self._get_live_price = get_live_price
        self._get_price_history = get_price_history
        self._record_local_price = record_local_price
        self._clock = clock

    def handle(self, message: AgentMessage) -> AgentMessage:
        now = self._clock.now()
        try:
            # Cada acción del mensaje corresponde a un caso de uso
            if message.action == Action.GET_LIVE_PRICE:
                live = self._get_live_price.execute()
                # La hora se entrega en la zona del caficultor (Lima)
                return message.reply_inform(live_to_dict(live, now.tzinfo), now)
            if message.action == Action.GET_PRICE_HISTORY:
                return message.reply_inform(self._history(message.content), now)
            if message.action == Action.RECORD_LOCAL_PRICE:
                command = RecordLocalPriceCommand(
                    cooperative=str(message.content.get("cooperative", "")),
                    coffee_type=str(message.content.get("coffee_type", "")),
                    paid_soles=str(message.content.get("paid_soles", "")),
                )
                observation = self._record_local_price.execute(command)
                return message.reply_inform(_observation_to_dict(observation, now.tzinfo), now)
            if message.action == Action.GET_LOCAL_PRICES:
                recent = self._record_local_price.recent()
                items = [_observation_to_dict(o, now.tzinfo) for o in recent]
                return message.reply_inform({"observations": items}, now)
        except MarketError as error:
            return message.reply_failure(str(error), now)
        return message.reply_failure(f"Acción no soportada: {message.action}", now)

    def _history(self, content: dict[str, Any]) -> dict[str, Any]:
        period = str(content.get("period", content.get("days", DEFAULT_HISTORY_DAYS)))
        if period == TODAY:
            zone = self._clock.now().tzinfo
            points = self._get_price_history.intraday()
            return {"period": TODAY, "points": [_intraday_to_dict(p, zone) for p in points]}
        daily = self._get_price_history.daily(int(period))
        return {"period": period, "points": [_point_to_dict(p) for p in daily]}


def live_to_dict(live: LivePrice, zone: tzinfo | None = None) -> dict[str, Any]:
    quoted_at = live.quoted_at.astimezone(zone) if zone else live.quoted_at
    return {
        "quoted_at": quoted_at.isoformat(),
        "date": quoted_at.date().isoformat(),
        "cents_per_pound": float(live.cents_per_pound),
        "price_soles": float(live.price.soles),
        "previous_close_soles": float(live.previous_close.soles) if live.previous_close else None,
        "change_soles": float(live.change_soles) if live.change_soles is not None else None,
        "change_pct": float(live.change_pct) if live.change_pct is not None else None,
        "unit": "S/ por quintal (46 kg)",
        "market": "Bolsa de Nueva York (ICE), café arábica",
        "market_open": live.market_open,
        "stale": live.stale,
        "sources": list(live.sources),
        "local_estimates": [_estimate_to_dict(e) for e in live.local_estimates],
    }


def _estimate_to_dict(estimate: LocalEstimate) -> dict[str, Any]:
    return {
        "coffee_type": estimate.coffee_type.value,
        "estimated_soles": float(estimate.estimated_soles),
        "ratio_pct": float((estimate.ratio * 100).quantize(Decimal("0.1"))),
        "observations": estimate.observations,
        "first_day": estimate.first_day.isoformat(),
        "last_day": estimate.last_day.isoformat(),
        "few_data": estimate.few_data,
    }


def _observation_to_dict(observation: LocalPriceObservation, zone: tzinfo | None) -> dict[str, Any]:
    observed_at = observation.observed_at.astimezone(zone) if zone else observation.observed_at
    return {
        "observed_at": observed_at.isoformat(),
        "cooperative": observation.cooperative,
        "coffee_type": observation.coffee_type.value,
        "paid_soles": float(observation.paid_soles),
        "exchange_soles": float(observation.exchange_soles),
        "ratio_pct": float((observation.ratio * 100).quantize(Decimal("0.1"))),
    }


def _point_to_dict(point: HistoryPoint) -> dict[str, Any]:
    return {"date": point.priced_on.isoformat(), "price_soles": float(point.price.soles)}


def _intraday_to_dict(point: IntradayPoint, zone: tzinfo | None) -> dict[str, Any]:
    quoted_at = point.quoted_at.astimezone(zone) if zone else point.quoted_at
    return {
        "time": quoted_at.isoformat(),
        "date": quoted_at.date().isoformat(),
        "price_soles": float(point.price.soles),
    }
