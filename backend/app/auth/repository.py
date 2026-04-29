"""Repositorio de usuarios para autenticación."""

from __future__ import annotations

from app.extensions import db
from app.models.usuario import Usuario


def find_user_by_email(email: str) -> dict | None:
    """Busca un usuario por email en la base de datos.

    Parameters
    ----------
    email:
        Email ya normalizado (lowercase, sin espacios).

    Returns
    -------
    dict | None
        Datos del usuario o ``None`` si no existe.
    """
    user: Usuario | None = db.session.query(Usuario).filter_by(email=email).first()
    if user is None:
        return None
    return {
        "id":            str(user.id),
        "empresa_id":    str(user.empresa_id),
        "email":         user.email,
        "password_hash": user.password_hash,
        "rol":           user.rol,
        "is_active":     user.activo,
    }
