from datetime import date, timedelta

_SATURDAY = 5


def next_business_days(start: date, count: int) -> list[date]:
    """Los siguientes `count` días hábiles después de `start`.

    La bolsa no opera sábados ni domingos.
    """
    days: list[date] = []
    current = start
    while len(days) < count:
        current += timedelta(days=1)
        if current.weekday() < _SATURDAY:
            days.append(current)
    return days
