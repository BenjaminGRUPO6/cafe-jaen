class ForecastingError(Exception):
    """Error de negocio del módulo de pronóstico."""


class NotEnoughHistoryError(ForecastingError):
    def __init__(self, required: int) -> None:
        super().__init__(f"Se necesitan al menos {required} precios históricos para pronosticar")


class ForecastNotAvailableError(ForecastingError):
    def __init__(self) -> None:
        super().__init__("Todavía no hay un pronóstico generado")
