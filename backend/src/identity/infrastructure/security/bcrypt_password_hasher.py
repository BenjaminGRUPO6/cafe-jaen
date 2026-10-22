import bcrypt


class BcryptPasswordHasher:
    """Implementa PasswordHasher con bcrypt (la contraseña nunca se guarda en texto plano)."""

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
