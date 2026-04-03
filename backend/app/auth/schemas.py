"""Esquema Marshmallow para el formulario de login."""

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate, validates

from app.common.sanitizers.email import sanitize_email
from app.common.sanitizers.text import sanitize_text


# Longitud máxima de contraseña aceptada (el frontend ya aplica el mismo límite)
_PASSWORD_MAX = 128
_PASSWORD_MIN = 8


class LoginSchema(Schema):
    """Valida y sanitiza las credenciales de inicio de sesión.

    Campos esperados del frontend:
    - email:    correo electrónico del usuario
    - password: contraseña en texto claro (se verificará contra el hash)
    - origen:   identificador del cliente ('web', 'app') — informativo
    """

    email = fields.String(
        required=True,
        validate=validate.Length(min=1, max=254),
        error_messages={"required": "El correo electrónico es obligatorio."},
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=_PASSWORD_MIN, max=_PASSWORD_MAX),
        error_messages={"required": "La contraseña es obligatoria."},
    )

    # Campo informativo — valor libre pero sanitizado; no afecta a la lógica
    origen = fields.String(
        load_default="web",
        validate=validate.Length(max=16),
    )

    class Meta:
        unknown = EXCLUDE

    # ── Pre-load: sanitización antes de la validación ───────────────────────

    @pre_load
    def sanitize_fields(self, data: dict, **_kwargs) -> dict:
        """Sanitiza los campos antes de que Marshmallow valide.

        - email:    strip tags + control chars + lowercase + sin espacios
        - password: strip tags + control chars (sin truncar, sin normalizar)
        - origen:   strip tags + control chars + trim
        """
        if "email" in data:
            raw = str(data["email"])
            # Eliminar tags HTML y control chars; el normalize final lo hace
            # sanitize_email (email-validator)
            data["email"] = sanitize_text(raw, max_length=254).strip().lower()

        if "password" in data:
            raw = str(data["password"])
            # Solo eliminamos etiquetas HTML y control chars.
            # NO se normaliza unicode ni se trunca aquí: el validate.Length
            # ya comprueba el máximo y la contraseña puede tener cualquier
            # carácter imprimible legítimo.
            data["password"] = raw.replace("<", "").replace(">", "")
            data["password"] = "".join(
                ch for ch in data["password"] if ord(ch) >= 0x20 or ch in ("\t",)
            )[:_PASSWORD_MAX]

        if "origen" in data:
            data["origen"] = sanitize_text(str(data["origen"]), max_length=16).strip()

        return data

    # ── Validaciones individuales ───────────────────────────────────────────

    @validates("email")
    def validate_email(self, value: str, **_kwargs) -> None:
        normalized = sanitize_email(value)
        if normalized is None:
            raise ValidationError("El correo electrónico no es válido.")

    @validates("password")
    def validate_password_printable(self, value: str, **_kwargs) -> None:
        """Garantiza que la contraseña solo contiene caracteres imprimibles."""
        if not value or not value.strip():
            raise ValidationError("La contraseña no puede estar vacía o ser solo espacios.")
