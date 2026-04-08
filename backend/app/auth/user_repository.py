"""Repositorio de usuarios para autenticación.

Interfaz de acceso a datos de usuario.
Actualmente usa un diccionario en memoria como stub — cuando se integre
SQLAlchemy u otro ORM bastará con reemplazar las funciones de este módulo
sin tocar el servicio ni las rutas.

Estructura esperada de un usuario:
    {
        "id":            str,         # identificador único (UUID o similar)
        "empresa_id":    str,         # UUID de la empresa a la que pertenece
        "email":         str,         # email normalizado (lowercase)
        "password_hash": str,         # hash bcrypt
        "is_active":     bool,        # cuenta habilitada
    }
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Stub en memoria — reemplazar por consulta a BD cuando esté disponible
# ---------------------------------------------------------------------------
# Las contraseñas deben generarse con auth.passwords.hash_password().
# Este dict es solo para que el endpoint funcione en desarrollo/pruebas.
_USERS_STUB: dict[str, dict] = {
    # Ejemplo: email="admin@example.com", password="changeme123"
    # Hash generado con: python -c "from app.auth.passwords import hash_password; print(hash_password('changeme123'))"
}


def find_user_by_email(email: str) -> dict | None:
    """Busca un usuario por email.

    Parameters
    ----------
    email:
        Email ya normalizado (lowercase, sin espacios).

    Returns
    -------
    dict | None
        Datos del usuario o ``None`` si no existe.
    """
    # TODO: reemplazar por consulta a BD, ej.:
    #   return db.session.query(User).filter_by(email=email).first()
    return _USERS_STUB.get(email)
