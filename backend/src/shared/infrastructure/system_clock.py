from datetime import date, datetime
from zoneinfo import ZoneInfo


class SystemClock:
    """Implementa el puerto Clock con la hora real de Lima."""

    def __init__(self, timezone: str = "America/Lima") -> None:
        self._zone = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._zone)

    def today(self) -> date:
        return self.now().date()
