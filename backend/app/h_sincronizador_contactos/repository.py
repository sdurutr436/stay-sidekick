"""Repositorio de acceso a datos para la integración Google OAuth.

Gestiona la persistencia de IntegracionGoogle (tokens cifrados) y las
preferencias de sincronización de contactos almacenadas en el JSONB
empresas.configuracion.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.extensions import db
from app.empresas.model import Empresa
from app.h_sincronizador_contactos.model import IntegracionGoogle


# ── IntegracionGoogle ─────────────────────────────────────────────────────


def get_google_integration(empresa_id: str) -> IntegracionGoogle | None:
    """Devuelve la integración Google de la empresa, o None si no existe."""
    return IntegracionGoogle.query.filter_by(empresa_id=empresa_id).first()


def upsert_google_tokens(
    empresa_id: str,
    access_token_cifrado: str | None,
    refresh_token_cifrado: str,
    token_expiry: datetime | None,
    alcance: str,
) -> IntegracionGoogle:
    """Crea o actualiza los tokens OAuth de Google para la empresa."""
    integracion = get_google_integration(empresa_id)
    if integracion:
        integracion.access_token_cifrado = access_token_cifrado
        integracion.refresh_token_cifrado = refresh_token_cifrado
        integracion.token_expiry = token_expiry
        integracion.alcance = alcance
        integracion.activo = True
        integracion.updated_at = datetime.now(timezone.utc)
    else:
        integracion = IntegracionGoogle(
            empresa_id=empresa_id,
            access_token_cifrado=access_token_cifrado,
            refresh_token_cifrado=refresh_token_cifrado,
            token_expiry=token_expiry,
            alcance=alcance,
            activo=True,
        )
        db.session.add(integracion)
    db.session.flush()
    return integracion


def update_access_token(
    integracion: IntegracionGoogle,
    access_token_cifrado: str,
    token_expiry: datetime | None,
) -> IntegracionGoogle:
    """Actualiza solo el access_token (tras un refresh)."""
    integracion.access_token_cifrado = access_token_cifrado
    integracion.token_expiry = token_expiry
    integracion.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return integracion


def delete_google_integration(integracion: IntegracionGoogle) -> None:
    """Elimina la integración Google de la empresa (desconexión)."""
    db.session.delete(integracion)
    db.session.flush()


# ── Preferencias de sincronización (empresas.configuracion JSONB) ─────────

_KEY_FORMATO_NOMBRE = "formato_nombre_contacto"
_KEY_INCLUIR_APARTAMENTO = "incluir_apartamento_contacto"
_KEY_FORMATO_APARTAMENTO = "formato_apartamento_contacto"
_KEY_INCLUIR_CHECKIN = "incluir_checkin_contacto"

DEFAULTS_PREFERENCIAS = {
    _KEY_FORMATO_NOMBRE: "nombre_apellidos",
    _KEY_INCLUIR_APARTAMENTO: True,
    _KEY_FORMATO_APARTAMENTO: "nota",
    _KEY_INCLUIR_CHECKIN: True,
}


def get_preferencias_contactos(empresa_id: str) -> dict:
    """Lee las preferencias de contactos del JSONB empresas.configuracion."""
    empresa = Empresa.query.filter_by(id=empresa_id).first()
    config = empresa.configuracion or {} if empresa else {}
    return {
        _KEY_FORMATO_NOMBRE: config.get(_KEY_FORMATO_NOMBRE, DEFAULTS_PREFERENCIAS[_KEY_FORMATO_NOMBRE]),
        _KEY_INCLUIR_APARTAMENTO: config.get(_KEY_INCLUIR_APARTAMENTO, DEFAULTS_PREFERENCIAS[_KEY_INCLUIR_APARTAMENTO]),
        _KEY_FORMATO_APARTAMENTO: config.get(_KEY_FORMATO_APARTAMENTO, DEFAULTS_PREFERENCIAS[_KEY_FORMATO_APARTAMENTO]),
        _KEY_INCLUIR_CHECKIN: config.get(_KEY_INCLUIR_CHECKIN, DEFAULTS_PREFERENCIAS[_KEY_INCLUIR_CHECKIN]),
    }


def save_preferencias_contactos(empresa_id: str, preferencias: dict) -> dict:
    """Persiste las preferencias de contactos en empresas.configuracion."""
    empresa = Empresa.query.filter_by(id=empresa_id).first()
    if empresa is None:
        return {}

    config = dict(empresa.configuracion or {})
    config.update(preferencias)
    empresa.configuracion = config
    empresa.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return get_preferencias_contactos(empresa_id)
