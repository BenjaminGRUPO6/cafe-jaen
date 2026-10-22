from datetime import timedelta

import jwt

from shared.domain.ports.clock import Clock

_ALGORITHM = "HS256"


class JwtTokenService:
    """Implementa TokenIssuer (identity) y TokenVerifier (shared) con JWT."""

    def __init__(self, secret: str, session_days: int, clock: Clock) -> None:
        self._secret = secret
        self._lifetime = timedelta(days=session_days)
        self._clock = clock

    def issue(self, user_id: str, role: str = "farmer") -> str:
        now = self._clock.now()
        payload = {"sub": user_id, "role": role, "iat": now, "exp": now + self._lifetime}
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def verify(self, token: str) -> str | None:
        subject = self._claims(token).get("sub")
        return subject if isinstance(subject, str) else None

    def role(self, token: str) -> str | None:
        role = self._claims(token).get("role")
        return role if isinstance(role, str) else None

    def _claims(self, token: str) -> dict[str, object]:
        try:
            return dict(jwt.decode(token, self._secret, algorithms=[_ALGORITHM]))
        except jwt.PyJWTError:
            return {}
