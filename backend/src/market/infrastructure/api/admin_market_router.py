"""Rutas del equipo para el catálogo de cooperativas, corregir precios y ver el historial.

Son tareas de administración (alta, edición y baja de datos), no comportamiento de los
agentes: por eso llaman a los casos de uso directamente y no pasan por el supervisor
(ver docs/decisiones/0010-administracion-sin-agentes.md).
"""

from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from market.application.correct_local_price import CorrectLocalPrice
from market.application.get_price_log import GetPriceLog
from market.application.manage_cooperatives import CooperativeData, ManageCooperatives
from market.domain.cooperative import Cooperative
from market.domain.errors import MarketError, NotFoundError

T = TypeVar("T")


class CooperativeRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    location: str = Field(default="Jaén", max_length=80)
    website: str | None = Field(default=None, max_length=200)
    active: bool = True


class CorrectionRequest(BaseModel):
    paid_soles: float = Field(gt=0, description="S/ por quintal")


def build_admin_market_router(
    cooperatives: ManageCooperatives,
    corrections: CorrectLocalPrice,
    price_log: GetPriceLog,
    require_user: Callable[..., str],
    require_admin: Callable[..., str],
) -> APIRouter:
    router = APIRouter(tags=["equipo"])
    admin = [Depends(require_admin)]

    @router.get("/cooperatives", dependencies=[Depends(require_user)])
    def active_cooperatives() -> dict[str, Any]:
        """Catálogo visible para el caficultor (vista «Por cooperativa»)."""
        return {"cooperatives": [_to_dict(c) for c in cooperatives.list() if c.active]}

    @router.get("/admin/cooperatives", dependencies=admin)
    def all_cooperatives() -> dict[str, Any]:
        return {"cooperatives": [_to_dict(c) for c in cooperatives.list()]}

    @router.post("/admin/cooperatives", dependencies=admin, status_code=status.HTTP_201_CREATED)
    def create_cooperative(body: CooperativeRequest) -> dict[str, Any]:
        return _to_dict(_handle(lambda: cooperatives.create(_data(body))))

    @router.put("/admin/cooperatives/{cooperative_id}", dependencies=admin)
    def update_cooperative(cooperative_id: int, body: CooperativeRequest) -> dict[str, Any]:
        return _to_dict(_handle(lambda: cooperatives.update(cooperative_id, _data(body))))

    @router.delete("/admin/cooperatives/{cooperative_id}", dependencies=admin)
    def remove_cooperative(cooperative_id: int) -> dict[str, str]:
        return {"result": _handle(lambda: cooperatives.remove(cooperative_id)).value}

    @router.patch("/admin/local-prices/{observation_id}", dependencies=admin)
    def correct_price(observation_id: int, body: CorrectionRequest) -> dict[str, Any]:
        corrected = _handle(lambda: corrections.edit(observation_id, str(body.paid_soles)))
        return {"id": observation_id, "ratio_pct": float(round(corrected.ratio * 100, 1))}

    @router.delete(
        "/admin/local-prices/{observation_id}",
        dependencies=admin,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_price(observation_id: int) -> Response:
        _handle(lambda: corrections.delete(observation_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.get("/admin/price-log", dependencies=admin)
    def log(limit: int = Query(60, ge=1, le=300)) -> dict[str, Any]:
        return {
            "entries": [
                {
                    "quoted_at": e.quoted_at.isoformat(),
                    "cents_per_pound": float(e.cents_per_pound),
                    "exchange_rate": float(e.exchange_rate) if e.exchange_rate else None,
                    "price_soles": float(e.price_soles) if e.price_soles else None,
                    "sources": list(e.sources),
                    "local_soles": {t.value: float(v) for t, v in e.local_soles.items()},
                }
                for e in price_log.execute(limit)
            ]
        }

    return router


def _handle(action: Callable[[], T]) -> T:
    """Convierte los errores del dominio en respuestas HTTP con el mensaje para el equipo."""
    try:
        return action()
    except NotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from None
    except MarketError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None


def _data(body: CooperativeRequest) -> CooperativeData:
    return CooperativeData(body.name, body.location, body.website, body.active)


def _to_dict(cooperative: Cooperative) -> dict[str, Any]:
    return {
        "id": cooperative.id,
        "name": cooperative.name,
        "location": cooperative.location,
        "website": cooperative.website,
        "active": cooperative.active,
    }
