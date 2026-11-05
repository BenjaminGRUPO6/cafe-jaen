from typing import Protocol

from market.domain.cooperative import Cooperative


class CooperativeRepository(Protocol):
    def all(self) -> list[Cooperative]:
        """Todo el catálogo, activas primero y por nombre."""
        ...

    def get(self, cooperative_id: int) -> Cooperative | None: ...

    def get_by_name(self, name: str) -> Cooperative | None:
        """Búsqueda sin distinguir mayúsculas, para no duplicar «CENFROCAFE» y «Cenfrocafe»."""
        ...

    def add(self, cooperative: Cooperative) -> Cooperative: ...

    def update(self, cooperative: Cooperative, previous_name: str) -> None:
        """Guarda los cambios; si cambió el nombre, también en los precios ya anotados."""
        ...

    def delete(self, cooperative_id: int) -> None: ...

    def has_prices(self, name: str) -> bool: ...
