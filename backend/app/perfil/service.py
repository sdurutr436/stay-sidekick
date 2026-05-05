"""Servicio del módulo de perfil de usuario."""

from __future__ import annotations

import logging

from marshmallow import ValidationError

from app.auth.passwords import hash_password, verify_password
from app.common.crypto import encrypt
from app.perfil import repository as repo
from app.perfil.schemas import CambiarPasswordSchema, ActualizarPMSSchema, ActualizarIASchema, XlsxApartamentosConfigSchema, NotifTardioConfigSchema

logger = logging.getLogger(__name__)

_schema_password    = CambiarPasswordSchema()
_schema_pms         = ActualizarPMSSchema()
_schema_ia          = ActualizarIASchema()
_schema_xlsx_config = XlsxApartamentosConfigSchema()
_schema_notif_tardio = NotifTardioConfigSchema()


def get_perfil(user_id: str) -> dict | None:
    usuario = repo.get_usuario_by_id(user_id)
    if not usuario:
        return None
    return {
        "email":               usuario.email,
        "rol":                 usuario.rol,
        "empresa_id":          str(usuario.empresa_id),
        "password_changed_at": usuario.password_changed_at.isoformat() if usuario.password_changed_at else None,
    }


def cambiar_password(user_id: str, json_data: dict) -> list[str]:
    try:
        data = _schema_password.load(json_data)
    except ValidationError as exc:
        return _flatten(exc.messages)

    usuario = repo.get_usuario_by_id(user_id)
    if not usuario:
        return ["Usuario no encontrado."]

    if not verify_password(data["password_actual"], usuario.password_hash):
        return ["La contraseña actual no es correcta."]

    repo.update_password(usuario, hash_password(data["password_nueva"]))
    return []


def get_integraciones(empresa_id: str) -> dict:
    data = repo.get_integraciones(empresa_id)
    pms    = data["pms"]
    google = data["google"]
    ia     = data["ia"]

    return {
        "pms": {
            "configurado": pms is not None and bool(pms.api_key_cifrada),
            "proveedor":   pms.proveedor if pms else None,
        },
        "google": {
            "configurado": google is not None and google.activo,
        },
        "ia": {
            "configurado": ia is not None and bool(ia.api_key_cifrada),
            "proveedor":   ia.proveedor if ia else None,
            "modelo":      ia.modelo if ia else None,
        },
    }


def actualizar_pms(empresa_id: str, json_data: dict) -> list[str]:
    try:
        data = _schema_pms.load(json_data)
    except ValidationError as exc:
        return _flatten(exc.messages)

    repo.upsert_pms(empresa_id, data["proveedor"], encrypt(data["api_key"]))
    return []


def actualizar_ia(empresa_id: str, json_data: dict) -> list[str]:
    try:
        data = _schema_ia.load(json_data)
    except ValidationError as exc:
        return _flatten(exc.messages)

    try:
        api_key_cifrada = encrypt(data["api_key"]) if data.get("api_key") else None
    except RuntimeError:
        return ["El servidor no tiene configurada la clave de cifrado (FERNET_KEY). Contacta con el administrador."]

    repo.upsert_ia(empresa_id, data["proveedor"], data.get("modelo"), api_key_cifrada)
    return []


def get_xlsx_apartamentos_config(empresa_id: str) -> dict:
    return repo.get_xlsx_apartamentos_config(empresa_id)


def save_xlsx_apartamentos_config(empresa_id: str, json_data: dict) -> list[str]:
    try:
        data = _schema_xlsx_config.load(json_data)
    except ValidationError as exc:
        return _flatten(exc.messages)
    repo.save_xlsx_apartamentos_config(empresa_id, data)
    return []


def get_notif_tardio_config(empresa_id: str) -> dict:
    return repo.get_notif_tardio_config(empresa_id)


def save_notif_tardio_config(empresa_id: str, json_data: dict) -> list[str]:
    try:
        data = _schema_notif_tardio.load(json_data)
    except ValidationError as exc:
        return _flatten(exc.messages)
    repo.save_notif_tardio_config(empresa_id, data)
    return []


def _flatten(messages: dict) -> list[str]:
    errors: list[str] = []
    for field, msgs in messages.items():
        if isinstance(msgs, list):
            errors.extend(f"{field}: {m}" for m in msgs)
    return errors
