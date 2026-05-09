"""Servicio del módulo de usuarios."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from marshmallow import ValidationError

from app.auth.passwords import hash_password
from app.common.sanitizers.email import sanitize_email
from app.empresas.model import Empresa
from app.extensions import db
from app.usuarios import repository
from app.usuarios.model import ROL_ADMIN
from app.usuarios.model import Usuario  # noqa: F401
from app.usuarios.schemas import UsuarioCreateSchema, UsuarioPatchSchema

_create_schema = UsuarioCreateSchema()
_patch_schema = UsuarioPatchSchema()

def _forced_change_at() -> datetime:
    """Contraseña con 60 días de antigüedad → fuerza cambio en el próximo login."""
    return datetime.now(timezone.utc) - timedelta(days=60)


def generar_password_temporal() -> str:
    return secrets.token_urlsafe(9).upper()


def _to_dict(u: Usuario) -> dict:
    return {
        "id": str(u.id),
        "email": u.email,
        "rol": u.rol,
        "activo": u.activo,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def _max_usuarios(empresa_id: str) -> int:
    empresa: Empresa | None = db.session.get(Empresa, empresa_id)
    if empresa is None:
        return 4
    return (empresa.configuracion or {}).get("max_usuarios", 4)


def _flatten_errors(messages: dict) -> list[str]:
    errors: list[str] = []
    for field, msgs in messages.items():
        if isinstance(msgs, list):
            errors.extend(f"{field}: {m}" for m in msgs)
        elif isinstance(msgs, dict):
            for sub_msgs in msgs.values():
                if isinstance(sub_msgs, list):
                    errors.extend(f"{field}: {m}" for m in sub_msgs)
    return errors


def listar_usuarios(empresa_id: str) -> dict:
    usuarios = repository.list_by_empresa(empresa_id)
    return {
        "usuarios": [_to_dict(u) for u in usuarios],
        "max_usuarios": _max_usuarios(empresa_id),
    }


def crear_usuario(empresa_id: str, json_data: dict) -> tuple[dict | None, list[str]]:
    try:
        clean = _create_schema.load(json_data)
    except ValidationError as exc:
        return None, _flatten_errors(exc.messages)

    email = sanitize_email(clean["email"])
    if email is None:
        return None, ["El correo electrónico no es válido."]

    max_u = _max_usuarios(empresa_id)
    if repository.count_total(empresa_id) >= max_u:
        return None, [f"Límite de usuarios alcanzado ({max_u})."]

    if repository.find_by_email(email):
        return None, ["El correo electrónico ya está en uso."]

    password_temp = generar_password_temporal()
    u = repository.create_usuario(
        empresa_id=empresa_id,
        email=email,
        rol=clean["rol"],
        password_hash=hash_password(password_temp),
        password_changed_at=_forced_change_at(),
    )
    db.session.commit()

    return {"usuario": _to_dict(u), "password_temporal": password_temp}, []


def eliminar_usuario(empresa_id: str, usuario_id: str, caller_id: str) -> list[str]:
    u = repository.get_by_id(usuario_id, empresa_id)
    if u is None:
        return ["Usuario no encontrado."]

    if str(u.id) == caller_id:
        return ["No puedes eliminar tu propia cuenta."]

    if u.rol == ROL_ADMIN and repository.count_admins(empresa_id) <= 1:
        return ["No se puede eliminar al único administrador."]

    repository.delete_usuario(u)
    db.session.commit()
    return []


def editar_rol(empresa_id: str, usuario_id: str, json_data: dict) -> tuple[dict | None, list[str]]:
    try:
        clean = _patch_schema.load(json_data)
    except ValidationError as exc:
        return None, _flatten_errors(exc.messages)

    u = repository.get_by_id(usuario_id, empresa_id)
    if u is None:
        return None, ["Usuario no encontrado."]

    nuevo_rol = clean["rol"]
    if u.rol == ROL_ADMIN and nuevo_rol != ROL_ADMIN:
        if repository.count_admins(empresa_id) <= 1:
            return None, ["No se puede quitar el rol al único administrador."]

    u = repository.update_usuario(u, rol=nuevo_rol)
    db.session.commit()
    return _to_dict(u), []


def resetear_password(empresa_id: str, usuario_id: str) -> tuple[dict | None, list[str]]:
    u = repository.get_by_id(usuario_id, empresa_id)
    if u is None:
        return None, ["Usuario no encontrado."]

    password_temp = generar_password_temporal()
    repository.update_usuario(
        u,
        password_hash=hash_password(password_temp),
        password_changed_at=_forced_change_at(),
    )
    db.session.commit()
    return {"password_temporal": password_temp}, []
