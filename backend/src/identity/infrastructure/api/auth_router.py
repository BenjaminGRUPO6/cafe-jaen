from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from identity.application.authenticate_user import AuthenticateUser
from identity.application.register_user import RegisterUser, RegisterUserCommand
from identity.domain.errors import IdentityError, InvalidCredentialsError
from identity.domain.ports.security import TokenIssuer


class RegisterRequest(BaseModel):
    invitation_code: str
    phone: str
    password: str
    consent_accepted: bool


class LoginRequest(BaseModel):
    phone: str
    password: str


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def build_auth_router(
    register: RegisterUser, authenticate: AuthenticateUser, tokens: TokenIssuer
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/register", status_code=status.HTTP_201_CREATED)
    def register_user(body: RegisterRequest) -> SessionResponse:
        try:
            user = register.execute(RegisterUserCommand(**body.model_dump()))
        except IdentityError as error:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
        # Se emite el token directamente: verificar la contraseña otra vez con bcrypt
        # duplicaría el costo del registro (detectado en la prueba de carga, T31)
        return SessionResponse(access_token=tokens.issue(user.id))

    @router.post("/login")
    def login(body: LoginRequest) -> SessionResponse:
        try:
            return SessionResponse(access_token=authenticate.execute(body.phone, body.password))
        except InvalidCredentialsError as error:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error)) from error

    return router
