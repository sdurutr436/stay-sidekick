"""Repositorio de acceso a datos para apartamentos y configuración PMS."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.h_maestro_apartamentos.model import Apartamento
from app.perfil.model import ConfiguracionPMS
from app.h_sincronizador_contactos.model import LogSincronizacion


# ── Apartamentos ─────────────────────────────────────────────────────────


def list_by_empresa(empresa_id: str, solo_activos: bool = True) -> list[Apartamento]:
    """Devuelve todos los apartamentos de una empresa."""
    query = Apartamento.query.filter_by(empresa_id=empresa_id)
    if solo_activos:
        query = query.filter_by(activo=True)
    return query.order_by(Apartamento.nombre).all()


def get_by_id(apartamento_id: str, empresa_id: str) -> Apartamento | None:
    """Busca un apartamento por su UUID, solo si pertenece a la empresa.

    Devuelve None (en lugar de propagar un error 500 de PostgreSQL) si
    ``apartamento_id`` no tiene formato UUID válido.
    """
    try:
        apartamento_uuid = uuid.UUID(apartamento_id)
    except ValueError:
        return None
    return Apartamento.query.filter_by(
        id=apartamento_uuid,
        empresa_id=empresa_id,
    ).first()


def get_by_id_externo(empresa_id: str, id_externo: str) -> Apartamento | None:
    """Busca un apartamento por empresa + id_externo (PMS / Excel)."""
    return Apartamento.query.filter_by(
        empresa_id=empresa_id,
        id_externo=id_externo,
    ).first()


def create(empresa_id: str, **kwargs) -> Apartamento:
    """Crea un nuevo apartamento."""
    apt = Apartamento(empresa_id=empresa_id, **kwargs)
    db.session.add(apt)
    db.session.flush()
    return apt


def update(apt: Apartamento, **kwargs) -> Apartamento:
    """Actualiza campos de un apartamento existente."""
    for key, value in kwargs.items():
        if hasattr(apt, key):
            setattr(apt, key, value)
    apt.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return apt


def soft_delete(apt: Apartamento) -> None:
    """Marca un apartamento como inactivo (soft delete)."""
    apt.activo = False
    apt.updated_at = datetime.now(timezone.utc)
    db.session.flush()


def upsert_from_external(
    empresa_id: str,
    id_externo: str,
    nombre: str,
    direccion: str | None,
    ciudad: str | None,
    pms_origen: str,
) -> tuple[Apartamento, bool]:
    """Inserta o actualiza un apartamento por empresa + id_externo.

    Returns
    -------
    tuple[Apartamento, bool]
        (apartamento, es_nuevo).
    """
    existing = get_by_id_externo(empresa_id, id_externo)

    if existing:
        existing.nombre = nombre
        existing.direccion = direccion or existing.direccion
        existing.ciudad = ciudad or existing.ciudad
        existing.activo = True
        existing.updated_at = datetime.now(timezone.utc)
        db.session.flush()
        return existing, False

    apt = Apartamento(
        empresa_id=empresa_id,
        id_externo=id_externo,
        nombre=nombre,
        direccion=direccion,
        ciudad=ciudad,
        pms_origen=pms_origen,
        activo=True,
    )
    db.session.add(apt)
    db.session.flush()
    return apt, True


# ── Configuración PMS ────────────────────────────────────────────────────


def get_pms_config(empresa_id: str) -> ConfiguracionPMS | None:
    """Devuelve la configuración PMS de la empresa."""
    return ConfiguracionPMS.query.filter_by(empresa_id=empresa_id).first()


def upsert_pms_config(
    empresa_id: str,
    proveedor: str,
    api_key_cifrada: str,
    endpoint: str | None = None,
) -> ConfiguracionPMS:
    """Crea o actualiza la configuración PMS de la empresa."""
    config = get_pms_config(empresa_id)

    if config:
        config.proveedor = proveedor
        config.api_key_cifrada = api_key_cifrada
        config.endpoint = endpoint
        config.activo = True
        config.updated_at = datetime.now(timezone.utc)
    else:
        config = ConfiguracionPMS(
            empresa_id=empresa_id,
            proveedor=proveedor,
            api_key_cifrada=api_key_cifrada,
            endpoint=endpoint,
            activo=True,
        )
        db.session.add(config)

    db.session.flush()
    return config


def delete_pms_config(config: ConfiguracionPMS) -> None:
    """Elimina la configuración PMS."""
    db.session.delete(config)
    db.session.flush()


# ── Logs de sincronización ───────────────────────────────────────────────


def create_sync_log(
    empresa_id: str,
    origen: str,
    estado: str,
    num_registros: int | None = None,
    detalle: str | None = None,
) -> LogSincronizacion:
    """Registra una operación de sincronización en el log de auditoría."""
    log = LogSincronizacion(
        empresa_id=empresa_id,
        origen=origen,
        estado=estado,
        num_registros=num_registros,
        detalle=detalle,
    )
    db.session.add(log)
    db.session.flush()
    return log
