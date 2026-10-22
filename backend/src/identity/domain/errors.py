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
        super().__init__("Celular o contraseña incorrectos")
