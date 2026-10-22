from datetime import date, datetime
from typing import Protocol


class Clock(Protocol):
    """Puerto de reloj: permite fijar la fecha en las pruebas."""

    def now(self) -> datetime: ...

    def today(self) -> date: ...
