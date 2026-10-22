"""Horario de la bolsa de Nueva York para el café arábica (ICE, contrato C)."""

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class MarketHours:
    """Indica si la bolsa está abierta. Valores por defecto: 04:15–13:30 de Nueva York.

    Se usa la hora de Nueva York para que el cambio de horario de verano no afecte:
    en Lima la apertura cae a las 03:15 o 04:15 según la época del año.
    """

    opens: time = time(4, 15)
    closes: time = time(13, 30)

    def is_open(self, moment: datetime) -> bool:
        local = moment.astimezone(NEW_YORK)
        if local.weekday() >= 5:  # sábado y domingo no hay negociación
            return False
        return self.opens <= local.time() < self.closes

    @staticmethod
    def trading_day(moment: datetime) -> date:
        """Día de negociación al que pertenece una cotización (fecha de Nueva York)."""
        return moment.astimezone(NEW_YORK).date()

    def close_of(self, day: date) -> datetime:
        """Hora de cierre de un día de negociación (para cierres diarios sin hora)."""
        return datetime.combine(day, self.closes, tzinfo=NEW_YORK)
