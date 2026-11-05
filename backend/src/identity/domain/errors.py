"""Errores del módulo de usuarios. Los mensajes se muestran tal cual al caficultor."""


class IdentityError(Exception):
    """Error de negocio del módulo identity."""


class InvalidInvitationCodeError(IdentityError):
    def __init__(self) -> None:
        super().__init__("El código de invitación no es válido o ya fue usado")


class PhoneAlreadyRegisteredError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Este celular ya está registrado")


class ConsentNotAcceptedError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Debes aceptar el consentimiento informado para continuar")


class WeakPasswordError(IdentityError):
    def __init__(self, min_length: int) -> None:
        super().__init__(f"La contraseña debe tener al menos {min_length} caracteres")


class InvalidPhoneError(IdentityError):
    def __init__(self) -> None:
        super().__init__("El celular debe tener 9 dígitos y empezar con 9")


class InvalidCredentialsError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Celular, correo o contraseña incorrectos")


class InvalidEmailError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Escribe un correo válido, por ejemplo nombre@gmail.com")


class EmailAlreadyRegisteredError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Este correo ya está registrado")


class AccountNotVerifiedError(IdentityError):
    def __init__(self, phone: str) -> None:
        super().__init__("Falta confirmar tu cuenta con el código que te enviamos")
        self.phone = phone  # la app abre «Verificar» con este celular (aunque ingrese por correo)


class InvalidVerificationCodeError(IdentityError):
    def __init__(self, remaining: int) -> None:
        super().__init__(f"El código no es correcto. Te quedan {remaining} intentos")


class VerificationExpiredError(IdentityError):
    def __init__(self) -> None:
        super().__init__("El código venció. Pide uno nuevo")


class TooManyAttemptsError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Demasiados intentos. Pide un código nuevo")


class ResendTooSoonError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Espera un minuto antes de pedir otro código")


class AlreadyVerifiedError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Esta cuenta ya está verificada: ingresa con tu celular y contraseña")


class UserNotFoundError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Esa cuenta no existe")


class CannotDeleteSelfError(IdentityError):
    def __init__(self) -> None:
        super().__init__("No puedes eliminar tu propia cuenta")


class LastAdminError(IdentityError):
    def __init__(self) -> None:
        super().__init__("Debe quedar al menos una cuenta del equipo")


class InvalidNameError(IdentityError):
    def __init__(self, limit: int) -> None:
        super().__init__(f"El nombre puede tener hasta {limit} caracteres")
