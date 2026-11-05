from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from support.application.support_inbox import FarmerSupport, TeamSupport
from support.domain.errors import SupportError
from support.domain.support_message import SupportMessage


class MessageRequest(BaseModel):
    text: str


def build_support_router(
    farmer: FarmerSupport,
    team: TeamSupport,
    describe_user: Callable[[str], dict[str, Any] | None],
    require_user: Callable[..., str],
    require_admin: Callable[..., str],
) -> APIRouter:
    """«Atención»: el caficultor escribe sus dudas y el equipo le responde.

    `describe_user` (celular y correo de la cuenta) lo entrega main.py desde el módulo de
    usuarios: así este módulo no depende de identity.
    """
    router = APIRouter(tags=["atención"])

    @router.get("/support/messages")
    def my_conversation(user_id: str = Depends(require_user)) -> dict[str, Any]:
        return {"messages": [_message(m) for m in farmer.conversation(user_id).messages]}

    @router.get("/support/unread")
    def my_unread(user_id: str = Depends(require_user)) -> dict[str, int]:
        return {"unread": farmer.unread_replies(user_id)}

    @router.post("/support/messages", status_code=status.HTTP_201_CREATED)
    def write(body: MessageRequest, user_id: str = Depends(require_user)) -> dict[str, Any]:
        try:
            return _message(farmer.write(user_id, body.text))
        except SupportError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None

    @router.get("/admin/support", dependencies=[Depends(require_admin)])
    def inbox() -> dict[str, Any]:
        threads = team.inbox()
        return {
            "unread": sum(t.unread for t in threads),
            "threads": [
                {
                    "user_id": t.user_id,
                    "user": describe_user(t.user_id),  # None si la cuenta fue eliminada
                    "last_text": t.last_text,
                    "last_at": t.last_at.isoformat(),
                    "last_author": t.last_author.value,
                    "unread": t.unread,
                }
                for t in threads
            ],
        }

    @router.get("/admin/support/{user_id}", dependencies=[Depends(require_admin)])
    def conversation(user_id: str) -> dict[str, Any]:
        return {
            "user": describe_user(user_id),
            "messages": [_message(m) for m in team.conversation(user_id).messages],
        }

    @router.post(
        "/admin/support/{user_id}",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_admin)],
    )
    def reply(user_id: str, body: MessageRequest) -> dict[str, Any]:
        try:
            return _message(team.reply(user_id, body.text))
        except SupportError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from None

    return router


def _message(message: SupportMessage) -> dict[str, Any]:
    return {
        "id": message.id,
        "author": message.author.value,
        "text": message.text,
        "created_at": message.created_at.isoformat(),
        "read": message.read,
    }
