"""Dependencias de FastAPI compartidas por los routers de todos los módulos.

Los routers se construyen con funciones fábrica (build_*_router) que reciben sus
dependencias de forma explícita desde main.py. Este archivo solo crea la
dependencia de autenticación a partir del puerto TokenVerifier.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.domain.ports.token_verifier import TokenVerifier

_bearer = HTTPBearer(auto_error=False)
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]


def build_require_user(
    verifier: TokenVerifier, is_active: Callable[[str], bool] | None = None
) -> Callable[[Credentials], str]:
    """Crea la dependencia que exige una sesión válida y devuelve el id del usuario.

    `is_active` comprueba que la cuenta siga existiendo: si el equipo la eliminó, su sesión
    deja de servir aunque el token aún no haya vencido.
    """

    def require_user(credentials: Credentials) -> str:
        user_id = verifier.verify(credentials.credentials) if credentials else None
        if user_id is None or (is_active is not None and not is_active(user_id)):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inicia sesión para continuar")
        return user_id

    return require_user


def build_require_admin(
    verifier: TokenVerifier, is_active: Callable[[str], bool] | None = None
) -> Callable[[Credentials], str]:
    """Dependencia para las rutas del equipo (anotar precios de cooperativas, HU12)."""
    require_user = build_require_user(verifier, is_active)

    def require_admin(credentials: Credentials) -> str:
        user_id = require_user(credentials)
        if credentials is None or verifier.role(credentials.credentials) != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el equipo puede hacer esto")
        return user_id

    return require_admin
