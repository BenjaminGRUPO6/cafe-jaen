from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from identity.application.list_participants import ListParticipants
from identity.application.manage_invitation_codes import (
    CodeNotFoundError,
    ManageInvitationCodes,
)
from identity.domain.errors import IdentityError


class GenerateCodesRequest(BaseModel):
    count: int


def build_participants_router(
    list_participants: ListParticipants,
    manage_codes: ManageInvitationCodes,
    require_admin: Callable[..., str],
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

    @router.get("/admin/invitation-codes")
    def invitation_codes() -> dict[str, Any]:
        return {
            "codes": [
                {"code": c.code, "used": c.is_used, "used_at": _iso(c.used_at)}
                for c in manage_codes.list()
            ]
        }

    @router.post("/admin/invitation-codes", status_code=status.HTTP_201_CREATED)
    def generate_codes(body: GenerateCodesRequest) -> dict[str, Any]:
        try:
            return {"codes": manage_codes.generate(body.count)}
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None

    @router.delete("/admin/invitation-codes/{code}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_code(code: str) -> Response:
        try:
            manage_codes.delete(code)
        except CodeNotFoundError as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from None
        except IdentityError as error:
            raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


def _iso(moment: datetime | None) -> str | None:
    return moment.isoformat() if moment else None
