"""Adaptadores del puerto EmailSender.

- Brevo (API HTTPS): funciona en el plan gratis de Render, que bloquea el envío por SMTP.
  Gratis hasta 300 correos al día; el remitente puede ser una cuenta de Gmail verificada.
- SMTP (por ejemplo Gmail con «contraseña de aplicación»): para correr la app en local.
- Sin proveedor: no envía nada; el código lo ve el equipo en «Participantes».
"""

import logging
import smtplib
from email.message import EmailMessage

import httpx

from identity.domain.ports.email_sender import EmailNotSentError, EmailSender

logger = logging.getLogger(__name__)
BREVO_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailSender:
    def __init__(self, api_key: str, sender_email: str, sender_name: str) -> None:
        self._api_key = api_key
        self._sender = {"email": sender_email, "name": sender_name}

    def send(self, to: str, subject: str, text: str) -> None:
        body = {
            "sender": self._sender,
            "to": [{"email": to}],
            "subject": subject,
            "textContent": text,
        }
        try:
            response = httpx.post(
                BREVO_URL, json=body, headers={"api-key": self._api_key}, timeout=10.0
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            logger.warning("Brevo no envió el correo: %s", error)
            raise EmailNotSentError(str(error)) from error


class SmtpEmailSender:
    def __init__(
        self, host: str, port: int, user: str, password: str, sender_email: str, sender_name: str
    ) -> None:
        self._host, self._port = host, port
        self._user, self._password = user, password
        self._from = f"{sender_name} <{sender_email}>"

    def send(self, to: str, subject: str, text: str) -> None:
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = self._from, to, subject
        message.set_content(text)
        try:
            with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(self._user, self._password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            logger.warning("SMTP no envió el correo: %s", error)
            raise EmailNotSentError(str(error)) from error


class DisabledEmailSender:
    """Sin proveedor configurado: el código queda solo para el equipo."""

    def send(self, to: str, subject: str, text: str) -> None:
        raise EmailNotSentError("No hay proveedor de correo configurado")


def build_email_sender(
    brevo_api_key: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    sender_email: str,
    sender_name: str,
) -> EmailSender:
    """Brevo si hay clave; si no, SMTP si hay usuario y contraseña; si no, ninguno."""
    if brevo_api_key and sender_email:
        return BrevoEmailSender(brevo_api_key, sender_email, sender_name)
    if smtp_user and smtp_password:
        return SmtpEmailSender(
            smtp_host, smtp_port, smtp_user, smtp_password, sender_email or smtp_user, sender_name
        )
    logger.warning("Sin proveedor de correo: los códigos solo se verán en «Participantes»")
    return DisabledEmailSender()
