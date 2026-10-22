class MarketError(Exception):
    """Error de negocio del módulo de mercado."""


class SourceUnavailableError(MarketError):
    """Una fuente externa (cotización o tipo de cambio) no respondió."""


class NoQuotationError(MarketError):
    def __init__(self) -> None:
        super().__init__("Ninguna fuente de cotización respondió")


class SourcesDisagreeError(MarketError):
    def __init__(self, sources: list[str]) -> None:
        super().__init__(f"Las fuentes no coinciden entre sí: {', '.join(sources)}")


class DuplicateQuotationError(MarketError):
    def __init__(self) -> None:
        super().__init__("No hay una cotización más reciente que la ya registrada")


class OutlierQuotationError(MarketError):
    def __init__(self, change_pct: float) -> None:
        super().__init__(f"Variación atípica de {change_pct:.1f} %: la cotización no se publica")


class PriceNotAvailableError(MarketError):
    def __init__(self) -> None:
        super().__init__("Todavía no hay precios registrados")


class InvalidLocalPriceError(MarketError):
    """El precio de una cooperativa no es válido (HU12)."""
