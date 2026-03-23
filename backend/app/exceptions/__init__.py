"""Excepciones personalizadas de la aplicación."""


class AppError(Exception):
    """Error base de la aplicación con código HTTP."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    """Error de validación del formulario."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("Error de validación", 422)
        self.errors = errors


class CaptchaError(AppError):
    """Error en la verificación del captcha."""

    def __init__(self) -> None:
        super().__init__("La verificación del captcha ha fallado.", 403)
