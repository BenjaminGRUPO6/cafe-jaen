from dataclasses import dataclass

NO_INFORMATION = (
    "No tengo esa información. Puedo ayudarte con el precio del café, su histórico, "
    "el pronóstico o evaluar una oferta."
)
SERVICE_UNAVAILABLE = "No pude obtener los datos en este momento. Intenta de nuevo en unos minutos."


@dataclass(frozen=True)
class Answer:
    """Respuesta del Agente Asesor al caficultor."""

    text: str
    sources: tuple[str, ...] = ()
    used_tool: str | None = None
