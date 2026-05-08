"""Repositorio de acceso a datos del módulo de usuarios."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.usuarios.model import ROL_ADMIN, Usuario


def list_by_empresa(empresa_id: str) -> list[Usuario]:
    return Usuario.query.filter_by(empresa_id=empresa_id).order_by(Usuario.created_at).all()


def get_by_id(usuario_id: str, empresa_id: str) -> Usuario | None:
    try:
        uid = uuid.UUID(usuario_id)
    except ValueError:
        return None
    return Usuario.query.filter_by(id=uid, empresa_id=empresa_id).first()


def count_total(empresa_id: str) -> int:
    return Usuario.query.filter_by(empresa_id=empresa_id).count()


def count_admins(empresa_id: str) -> int:
    return Usuario.query.filter_by(empresa_id=empresa_id, rol=ROL_ADMIN).count()


def find_by_email(email: str) -> Usuario | None:
    return Usuario.query.filter_by(email=email).first()


def create_usuario(
    empresa_id: str,
    email: str,
    rol: str,
    password_hash: str,
    password_changed_at: datetime,
) -> Usuario:
    u = Usuario(
        empresa_id=empresa_id,
        email=email,
        rol=rol,
        password_hash=password_hash,
        password_changed_at=password_changed_at,
    )
    db.session.add(u)
    db.session.flush()
    return u


def update_usuario(u: Usuario, **kwargs) -> Usuario:
    for key, value in kwargs.items():
        setattr(u, key, value)
    u.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return u


def delete_usuario(u: Usuario) -> None:
    db.session.delete(u)
    db.session.flush()
