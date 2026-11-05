from typing import Protocol

from identity.domain.user import User


class CodeNotSentError(Exception):
    """El canal no pudo entregar el código (sin configurar, sin destino o proveedor caído)."""


class CodeSender(Protocol):
    """Puerto de salida: entrega el código de verificación por un canal (WhatsApp o correo).

    La aplicación prueba los canales en orden de prioridad: primero el celular.
    """

    channel: str  # «whatsapp» o «email»

    def send(self, user: User, code: str) -> None: ...
