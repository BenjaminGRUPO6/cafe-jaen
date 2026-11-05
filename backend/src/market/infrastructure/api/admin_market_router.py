"""Rutas del equipo para el catálogo de cooperativas, corregir precios y ver el historial.

Son tareas de administración (alta, edición y baja de datos), no comportamiento de los
agentes: por eso llaman a los casos de uso directamente y no pasan por el supervisor
(ver docs/decisiones/0010-administracion-sin-agentes.md).
"""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from market.application.correct_local_price import CorrectLocalPrice
from market.application.get_price_log import GetPriceLog, PriceLogEntry
from market.application.manage_cooperatives import CooperativeData, ManageCooperatives
from market.application.manage_synthetic_data import ManageSyntheticData, SyntheticStatus
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
    synthetic: ManageSyntheticData,
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

    # ---- precios sintéticos de demostración (solo el equipo los carga o los borra)
    @router.get("/admin/synthetic-data", dependencies=admin)
    def synthetic_status() -> dict[str, int]:
        return _status(synthetic.status())

    @router.post("/admin/synthetic-data", dependencies=admin)
    def load_synthetic() -> dict[str, int]:
        return _status(_handle(synthetic.load))

    @router.delete("/admin/synthetic-data", dependencies=admin)
    def remove_synthetic() -> dict[str, int]:
        return _status(_handle(synthetic.remove))

    @router.get("/admin/price-log", dependencies=admin)
    def log(day: date | None = None) -> dict[str, Any]:
        """Historial de un día (hora de Lima); sin `day`, el de hoy."""
        log = price_log.execute(day)
        return {
            "entries": [_entry(e) for e in log.entries],
            "ranking": [
                {
                    "source": r.source,
                    "consultations": r.consultations,
                    "answered": r.answered,
                    "used": r.used,
                    "discarded": r.discarded,
                    "avg_delay_minutes": r.avg_delay_minutes,
                    "avg_deviation_pct": r.avg_deviation_pct,
                    "score": r.score,
                }
                for r in log.ranking
            ],
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


def _entry(e: PriceLogEntry) -> dict[str, Any]:
    return {
        "quoted_at": e.at.isoformat(),
        "published": e.published,
        "outcome": e.outcome.value,
        "detail": e.detail,
        "cents_per_pound": _num(e.cents_per_pound),
        "median_cents": _num(e.median_cents),
        "exchange_rate": _num(e.exchange_rate),
        "price_soles": _num(e.price_soles),
        "sources": list(e.sources),
        "local_soles": {t.value: float(v) for t, v in e.local_soles.items()},
        "readings": [
            {
                "source": r.source,
                "status": r.status.value,
                "cents_per_pound": _num(r.cents_per_pound),
                "quoted_at": r.quoted_at.isoformat() if r.quoted_at else None,
                "deviation_pct": _num(r.deviation_pct),
                "detail": r.detail,
                "has_exchange_time": r.has_exchange_time,
            }
            for r in e.readings
        ],
    }


def _status(status: SyntheticStatus) -> dict[str, int]:
    return {"cooperatives": status.cooperatives, "observations": status.observations}


def _num(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


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
