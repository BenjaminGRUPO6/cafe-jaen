from dataclasses import replace
from decimal import Decimal, InvalidOperation

from market.domain.errors import InvalidLocalPriceError, NotFoundError
from market.domain.local_price import LocalPriceObservation
from market.domain.ports.price_repository import PriceRepository


class CorrectLocalPrice:
    """El equipo corrige o borra un precio anotado por error (HU12).

    Al corregir se conserva la bolsa de aquel momento: el porcentaje se recalcula con ella y
    pasa por las mismas validaciones que al anotarlo.
    """

    def __init__(self, repository: PriceRepository) -> None:
        self._repository = repository

    def edit(self, observation_id: int, paid_soles: str) -> LocalPriceObservation:
        current = self._get(observation_id)
        try:
            paid = Decimal(paid_soles)
        except InvalidOperation:
            raise InvalidLocalPriceError("Revisa el precio") from None
        corrected = replace(current, paid_soles=paid)  # valida el nuevo porcentaje
        self._repository.update_local_paid(observation_id, paid)
        return corrected

    def delete(self, observation_id: int) -> None:
        self._get(observation_id)
        self._repository.delete_local_observation(observation_id)

    def _get(self, observation_id: int) -> LocalPriceObservation:
        observation = self._repository.get_local_observation(observation_id)
        if observation is None:
            raise NotFoundError("Ese precio ya no existe")
        return observation
