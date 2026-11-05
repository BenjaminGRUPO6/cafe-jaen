"""Catálogo de cooperativas de Jaén que el equipo consulta (HU12).

Los precios anotados guardan el nombre de la cooperativa: el catálogo asegura que siempre se
escriba igual y permite ocultar las que ya no se consultan sin perder su historial.
"""

from dataclasses import dataclass, replace

from market.domain.errors import InvalidCooperativeError

MAX_NAME_LENGTH = 80
MAX_LOCATION_LENGTH = 80
MAX_WEBSITE_LENGTH = 200


@dataclass(frozen=True)
class Cooperative:
    id: int | None
    name: str
    location: str = "Jaén"
    website: str | None = None
    active: bool = True  # las archivadas no aparecen al anotar precios, pero conservan su historial

    def __post_init__(self) -> None:
        if not 2 <= len(self.name.strip()) <= MAX_NAME_LENGTH:
            raise InvalidCooperativeError(
                f"El nombre debe tener entre 2 y {MAX_NAME_LENGTH} caracteres"
            )
        if len(self.location.strip()) > MAX_LOCATION_LENGTH:
            raise InvalidCooperativeError("La ubicación es demasiado larga")
        if self.website and (
            not self.website.startswith(("http://", "https://"))
            or len(self.website) > MAX_WEBSITE_LENGTH
        ):
            raise InvalidCooperativeError("La web debe empezar con http:// o https://")

    @staticmethod
    def create(name: str, location: str, website: str | None) -> "Cooperative":
        return Cooperative(None, name.strip(), location.strip() or "Jaén", _clean(website))

    def edit(self, name: str, location: str, website: str | None, active: bool) -> "Cooperative":
        return replace(
            self,
            name=name.strip(),
            location=location.strip() or "Jaén",
            website=_clean(website),
            active=active,
        )


def _clean(website: str | None) -> str | None:
    return website.strip() or None if website else None
