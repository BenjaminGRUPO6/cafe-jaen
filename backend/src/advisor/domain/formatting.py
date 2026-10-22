"""Formato de números al estilo peruano: coma decimal y sin separador de miles."""


def soles(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def percent(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def spanish_date(iso_date: str) -> str:
    year, month, day = iso_date.split("-")
    return f"{day}/{month}/{year}"
