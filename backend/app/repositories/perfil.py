"""Repositorio de datos para el módulo de perfil de usuario."""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db
from app.usuarios.model import Usuario
from app.models.integraciones import ConfiguracionPMS, ConfiguracionIA, IntegracionGoogle


def get_usuario_by_id(user_id: str) -> Usuario | None:
    return db.session.get(Usuario, user_id)


def update_password(user: Usuario, new_hash: str) -> None:
    user.password_hash = new_hash
    user.password_changed_at = datetime.now(timezone.utc)
    db.session.commit()


def get_integraciones(empresa_id: str) -> dict:
    pms    = db.session.query(ConfiguracionPMS).filter_by(empresa_id=empresa_id).first()
    google = db.session.query(IntegracionGoogle).filter_by(empresa_id=empresa_id).first()
    ia     = db.session.query(ConfiguracionIA).filter_by(empresa_id=empresa_id).first()
    return {"pms": pms, "google": google, "ia": ia}


def upsert_pms(empresa_id: str, proveedor: str, api_key_cifrada: str) -> None:
    pms = db.session.query(ConfiguracionPMS).filter_by(empresa_id=empresa_id).first()
    if pms:
        pms.proveedor       = proveedor
        pms.api_key_cifrada = api_key_cifrada
        pms.activo          = True
    else:
        db.session.add(ConfiguracionPMS(
            empresa_id=empresa_id,
            proveedor=proveedor,
            api_key_cifrada=api_key_cifrada,
        ))
    db.session.commit()


def upsert_ia(empresa_id: str, proveedor: str, modelo: str | None, api_key_cifrada: str | None) -> None:
    ia = db.session.query(ConfiguracionIA).filter_by(empresa_id=empresa_id).first()
    if ia:
        ia.proveedor       = proveedor
        ia.modelo          = modelo
        ia.api_key_cifrada = api_key_cifrada
        ia.activo          = True
    else:
        db.session.add(ConfiguracionIA(
            empresa_id=empresa_id,
            proveedor=proveedor,
            modelo=modelo,
            api_key_cifrada=api_key_cifrada,
        ))
    db.session.commit()
