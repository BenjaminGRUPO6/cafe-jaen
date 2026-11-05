"""Errores del módulo de atención. Los mensajes se muestran tal cual al caficultor."""


class SupportError(Exception):
    """Error de negocio del módulo support."""


class EmptyMessageError(SupportError):
    def __init__(self) -> None:
        super().__init__("Escribe tu mensaje antes de enviarlo")


class MessageTooLongError(SupportError):
    def __init__(self, limit: int) -> None:
        super().__init__(f"El mensaje puede tener hasta {limit} caracteres")
