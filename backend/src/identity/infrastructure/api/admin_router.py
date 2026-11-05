from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends

from identity.application.list_participants import ListParticipants


def build_participants_router(
    list_participants: ListParticipants, require_admin: Callable[..., str]
) -> APIRouter:
    """Rutas del equipo de investigación sobre los participantes (solo administrador)."""
    router = APIRouter(tags=["equipo"], dependencies=[Depends(require_admin)])

    @router.get("/admin/participants")
    def participants() -> dict[str, Any]:
        report = list_participants.execute()
        return {
            "codes": {"total": report.codes.total, "used": report.codes.used},
            "participants": [
                {
                    "phone": p.phone,
                    "role": p.role.value,
                    "registered_at": _iso(p.registered_at),
                    "invitation_code": p.invitation_code,
                    "last_login_at": _iso(p.last_login_at),
                }
                for p in report.participants
            ],
        }

    return router


def _iso(moment: datetime | None) -> str | None:
    return moment.isoformat() if moment else None
