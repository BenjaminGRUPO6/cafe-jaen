"""Adaptadores del puerto CodeSender: por dónde llega el código de verificación.

Prioridad (la arma `build_code_senders`):
1. WhatsApp al celular, con la API oficial de WhatsApp Business (Meta Cloud API) y una
   plantilla de autenticación aprobada. Necesita WHATSAPP_TOKEN y WHATSAPP_PHONE_NUMBER_ID.
2. Correo, si la persona lo dio: Brevo (API HTTPS, sirve en el plan gratis de Render, que
   bloquea SMTP) o, en local, Gmail por SMTP con una «contraseña de aplicación».
Si ningún canal está configurado o todos fallan, el código lo ve el equipo en «Participantes»
y se lo envía por WhatsApp desde su propio celular.
"""

import logging
import smtplib
from collections.abc import Mapping
from email.message import EmailMessage

import httpx

from identity.domain.ports.code_sender import CodeNotSentError, CodeSender
from identity.domain.user import User
from identity.domain.verification import LIFETIME

logger = logging.getLogger(__name__)
GRAPH_URL = "https://graph.facebook.com/v21.0/{phone_number_id}/messages"
BREVO_URL = "https://api.brevo.com/v3/smtp/email"
PERU_PREFIX = "51"
SUBJECT = "Tu código para Café Jaén"


class WhatsAppCloudCodeSender:
    """Envía el código con una plantilla de autenticación de WhatsApp Business."""

    channel = "whatsapp"

    def __init__(self, token: str, phone_number_id: str, template: str, language: str) -> None:
        self._token = token
        self._url = GRAPH_URL.format(phone_number_id=phone_number_id)
        self._template = template
        self._language = language

    def send(self, user: User, code: str) -> None:
        # Plantilla de autenticación: el código va en el cuerpo y en el botón «Copiar código»
        body = {
            "messaging_product": "whatsapp",
            "to": PERU_PREFIX + user.phone.value,
            "type": "template",
            "template": {
                "name": self._template,
                "language": {"code": self._language},
                "components": [
                    {"type": "body", "parameters": [{"type": "text", "text": code}]},
                    {
                        "type": "button",
                        "sub_type": "url",
                        "index": "0",
                        "parameters": [{"type": "text", "text": code}],
                    },
                ],
            },
        }
        _post(self._url, body, {"Authorization": f"Bearer {self._token}"}, "WhatsApp")


class BrevoCodeSender:
    channel = "email"

    def __init__(self, api_key: str, sender_email: str, sender_name: str) -> None:
        self._api_key = api_key
        self._sender = {"email": sender_email, "name": sender_name}

    def send(self, user: User, code: str) -> None:
        if user.email is None:
            raise CodeNotSentError("sin correo")
        body = {
            "sender": self._sender,
            "to": [{"email": user.email.value}],
            "subject": SUBJECT,
            "textContent": email_text(code),
        }
        _post(BREVO_URL, body, {"api-key": self._api_key}, "Brevo")


class SmtpCodeSender:
    channel = "email"

    def __init__(
        self, host: str, port: int, user: str, password: str, sender_email: str, sender_name: str
    ) -> None:
        self._host, self._port = host, port
        self._user, self._password = user, password
        self._from = f"{sender_name} <{sender_email}>"

    def send(self, user: User, code: str) -> None:
        if user.email is None:
            raise CodeNotSentError("sin correo")
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = self._from, user.email.value, SUBJECT
        message.set_content(email_text(code))
        try:
            with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
                smtp.starttls()
                smtp.login(self._user, self._password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as error:
            logger.warning("SMTP no envió el código: %s", error)
            raise CodeNotSentError(str(error)) from error


def email_text(code: str) -> str:
    minutes = int(LIFETIME.total_seconds() // 60)
    return (
        f"Hola:\n\nTu código para activar tu cuenta en Café Jaén es: {code}\n\n"
        f"Escríbelo en la aplicación. Vence en {minutes} minutos.\n"
        "Si no creaste esta cuenta, ignora este mensaje.\n\n"
        "Equipo Café Jaén — Universidad Privada Antenor Orrego"
    )


def _post(url: str, body: Mapping[str, object], headers: dict[str, str], name: str) -> None:
    try:
        response = httpx.post(url, json=body, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as error:
        logger.warning("%s no envió el código: %s", name, error)
        raise CodeNotSentError(str(error)) from error


def build_code_senders(
    *,
    whatsapp_token: str,
    whatsapp_phone_number_id: str,
    whatsapp_template: str,
    whatsapp_language: str,
    brevo_api_key: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    sender_email: str,
    sender_name: str,
) -> list[CodeSender]:
    """Los canales configurados, en orden de prioridad (primero el celular)."""
    senders: list[CodeSender] = []
    if whatsapp_token and whatsapp_phone_number_id:
        senders.append(
            WhatsAppCloudCodeSender(
                whatsapp_token, whatsapp_phone_number_id, whatsapp_template, whatsapp_language
            )
        )
    if brevo_api_key and sender_email:
        senders.append(BrevoCodeSender(brevo_api_key, sender_email, sender_name))
    elif smtp_user and smtp_password:
        senders.append(
            SmtpCodeSender(
                smtp_host,
                smtp_port,
                smtp_user,
                smtp_password,
                sender_email or smtp_user,
                sender_name,
            )
        )
    if not senders:
        logger.warning(
            "Sin WhatsApp ni correo configurados: el código solo se verá en «Participantes»"
        )
    return senders
