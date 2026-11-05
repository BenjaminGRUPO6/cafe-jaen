from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from identity.application.authenticate_user import AuthenticateUser
from identity.application.email_verification import SendVerificationCode, VerifyAccount
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.domain.errors import (
    AccountNotVerifiedError,
    IdentityError,
    InvalidCredentialsError,
)


class RegisterRequest(BaseModel):
    invitation_code: str
    phone: str
    email: str
    password: str
    consent_accepted: bool


class LoginRequest(BaseModel):
    phone: str
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
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/register", status_code=status.HTTP_201_CREATED)
    def register_user(body: RegisterRequest) -> dict[str, Any]:
        try:
            user = register.execute(RegisterUserCommand(**body.model_dump()))
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        # Sin sesión todavía: primero debe escribir el código que llegó a su correo
        email_sent = send_code.for_new_user(user)
        return {
            "verification_required": True,
            "phone": user.phone.value,
            "email": user.email.masked() if user.email else None,
            "email_sent": email_sent,
        }

    @router.post("/verify")
    def verify_account(body: VerifyRequest) -> SessionResponse:
        try:
            return SessionResponse(access_token=verify.execute(body.phone, body.code))
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    @router.post("/resend")
    def resend_code(body: ResendRequest) -> dict[str, Any]:
        try:
            user, email_sent = send_code.resend(body.phone)
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        return {"email": user.email.masked() if user.email else None, "email_sent": email_sent}

    @router.post("/login")
    def login(body: LoginRequest) -> SessionResponse:
        try:
            return SessionResponse(access_token=authenticate.execute(body.phone, body.password))
        except AccountNotVerifiedError as error:
            # 403: la contraseña es correcta pero falta el código (la app abre «Verificar»)
            raise HTTPException(status.HTTP_403_FORBIDDEN, str(error)) from error
        except InvalidCredentialsError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error

    return router
