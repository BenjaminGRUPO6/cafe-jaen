from dataclasses import dataclass
from enum import StrEnum

from market.domain.cooperative import Cooperative
from market.domain.errors import InvalidCooperativeError, NotFoundError
from market.domain.ports.cooperative_repository import CooperativeRepository


@dataclass(frozen=True)
class CooperativeData:
    name: str
    location: str = "Jaén"
    website: str | None = None
    active: bool = True


class Removal(StrEnum):
    DELETED = "deleted"  # no tenía precios: se borra del catálogo
    ARCHIVED = "archived"  # tenía precios: se oculta para no perder el historial


class ManageCooperatives:
    """El equipo agrega, edita y quita cooperativas del catálogo (pantalla «Equipo»)."""

    def __init__(self, repository: CooperativeRepository) -> None:
        self._repository = repository

    def list(self) -> list[Cooperative]:
        return self._repository.all()

    def create(self, data: CooperativeData) -> Cooperative:
        cooperative = Cooperative.create(data.name, data.location, data.website)
        self._ensure_unique(cooperative.name)
        return self._repository.add(cooperative)

    def update(self, cooperative_id: int, data: CooperativeData) -> Cooperative:
        current = self._get(cooperative_id)
        edited = current.edit(data.name, data.location, data.website, data.active)
        if edited.name.lower() != current.name.lower():
            self._ensure_unique(edited.name)
        self._repository.update(edited, previous_name=current.name)
        return edited

    def remove(self, cooperative_id: int) -> Removal:
        current = self._get(cooperative_id)
        if self._repository.has_prices(current.name):
            self._repository.update(
                current.edit(current.name, current.location, current.website, active=False),
                previous_name=current.name,
            )
            return Removal.ARCHIVED
        self._repository.delete(cooperative_id)
        return Removal.DELETED

    def _get(self, cooperative_id: int) -> Cooperative:
        cooperative = self._repository.get(cooperative_id)
        if cooperative is None:
            raise NotFoundError("La cooperativa ya no existe")
        return cooperative

    def _ensure_unique(self, name: str) -> None:
        if self._repository.get_by_name(name) is not None:
            raise InvalidCooperativeError(f"«{name}» ya está en el catálogo")
