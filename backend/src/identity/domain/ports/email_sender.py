from typing import Protocol


class EmailSender(Protocol):
    """Puerto de salida: envía un correo de texto. Si no se pudo, lanza EmailNotSentError."""

    def send(self, to: str, subject: str, text: str) -> None: ...


class EmailNotSentError(Exception):
    """El proveedor de correo no aceptó el envío (o no está configurado)."""
