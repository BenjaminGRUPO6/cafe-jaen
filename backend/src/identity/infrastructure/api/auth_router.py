from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import AliasChoices, BaseModel, Field

from identity.application.authenticate_user import AuthenticateUser
from identity.application.get_profile import GetProfile
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.application.verify_account import SendVerificationCode, VerifyAccount
from identity.domain.errors import (
    AccountNotVerifiedError,
    IdentityError,
    InvalidCredentialsError,
)
from identity.domain.user import User


class RegisterRequest(BaseModel):
    invitation_code: str
    phone: str
    email: str = ""  # opcional
    name: str = ""  # opcional
    password: str
    consent_accepted: bool


class LoginRequest(BaseModel):
    # Celular o correo; se acepta también «phone» (versiones anteriores de la app)
    identifier: str = Field(validation_alias=AliasChoices("identifier", "phone"))
    password: str


class VerifyRequest(BaseModel):
    phone: str
    code: str


class ResendRequest(BaseModel):
    phone: str


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def build_auth_router(
    register: RegisterUser,
    authenticate: AuthenticateUser,
    send_code: SendVerificationCode,
    verify: VerifyAccount,
    get_profile: GetProfile,
    require_user: Callable[..., str],
    team_whatsapp: str,
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    def delivery(user: User, channel: str | None) -> dict[str, Any]:
        """A dónde salió el código y, si no salió, el WhatsApp del equipo para pedirlo."""
        return {
            "phone": user.phone.value,
            "email": user.email.masked() if user.email else None,
            "delivered_by": channel,
            "team_whatsapp": team_whatsapp or None,
        }

    @router.post("/register", status_code=status.HTTP_201_CREATED)
    def register_user(body: RegisterRequest) -> dict[str, Any]:
        try:
            user = register.execute(RegisterUserCommand(**body.model_dump()))
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        # Sin sesión todavía: primero debe escribir el código que llegó a su celular
        return {"verification_required": True, **delivery(user, send_code.for_new_user(user))}

    @router.post("/verify")
    def verify_account(body: VerifyRequest) -> SessionResponse:
        try:
            return SessionResponse(access_token=verify.execute(body.phone, body.code))
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    @router.post("/resend")
    def resend_code(body: ResendRequest) -> dict[str, Any]:
        try:
            user, channel = send_code.resend(body.phone)
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        return delivery(user, channel)

    @router.post("/login", response_model=None)
    def login(body: LoginRequest) -> SessionResponse | JSONResponse:
        try:
            return SessionResponse(
                access_token=authenticate.execute(body.identifier, body.password)
            )
        except AccountNotVerifiedError as error:
            # 403: la contraseña es correcta pero falta el código; la app abre «Verificar»
            return JSONResponse(
                {"detail": str(error), "phone": error.phone},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        except InvalidCredentialsError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error

    @router.get("/me")
    def me(user_id: str = Depends(require_user)) -> dict[str, Any]:
        try:
            user = get_profile.execute(user_id)
        except IdentityError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error
        return {
            "name": user.name,
            "display_name": user.display_name,
            "phone": user.phone.value,
            "email": user.email.value if user.email else None,
            "role": user.role.value,
        }

    return router
