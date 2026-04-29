"""Lógica de negocio del módulo de apartamentos.

Orquesta las operaciones CRUD, sincronización con Smoobu e importación
XLSX, delegando en el repositorio y registrando logs de auditoría.
"""

import logging

import requests
from marshmallow import ValidationError

from app.extensions import db
from app.common.crypto import decrypt, encrypt
from app.h_maestro_apartamentos import repository as repo
from app.h_maestro_apartamentos.schemas import (
    ApartamentoCreateSchema,
    ApartamentoUpdateSchema,
    PMSConfigSchema,
)
from app.h_maestro_apartamentos.smoobu_client import SmoobuClient
from app.h_maestro_apartamentos.xlsx_parser import parse_xlsx
from app.h_maestro_apartamentos.model import ORIGEN_SMOOBU, ORIGEN_XLSX, ORIGEN_MANUAL

logger = logging.getLogger(__name__)

_create_schema = ApartamentoCreateSchema()
_update_schema = ApartamentoUpdateSchema()
_pms_config_schema = PMSConfigSchema()


# ── Helpers ──────────────────────────────────────────────────────────────


def _apt_to_dict(apt) -> dict:
    """Serializa un Apartamento a dict para la respuesta JSON."""
    return {
        "id": str(apt.id),
        "empresa_id": str(apt.empresa_id),
        "id_externo": apt.id_externo,
        "nombre": apt.nombre,
        "direccion": apt.direccion,
        "ciudad": apt.ciudad,
        "pms_origen": apt.pms_origen,
        "activo": apt.activo,
        "created_at": apt.created_at.isoformat() if apt.created_at else None,
        "updated_at": apt.updated_at.isoformat() if apt.updated_at else None,
    }


# ── CRUD ─────────────────────────────────────────────────────────────────


def list_apartamentos(empresa_id: str) -> list[dict]:
    apts = repo.list_by_empresa(empresa_id)
    return [_apt_to_dict(a) for a in apts]


def get_apartamento(empresa_id: str, apartamento_id: str) -> tuple[dict | None, str | None]:
    apt = repo.get_by_id(apartamento_id, empresa_id)
    if not apt:
        return None, "Apartamento no encontrado."
    return _apt_to_dict(apt), None


def create_apartamento(empresa_id: str, json_data: dict) -> tuple[dict | None, list[str]]:
    try:
        clean = _create_schema.load(json_data)
    except ValidationError as exc:
        return None, _flatten(exc.messages)

    apt = repo.create(
        empresa_id=empresa_id,
        id_externo=clean.get("id_externo"),
        nombre=clean["nombre"],
        direccion=clean.get("direccion"),
        ciudad=clean.get("ciudad"),
        pms_origen=ORIGEN_MANUAL,
    )
    db.session.commit()
    return _apt_to_dict(apt), []


def update_apartamento(
    empresa_id: str, apartamento_id: str, json_data: dict
) -> tuple[dict | None, list[str]]:
    apt = repo.get_by_id(apartamento_id, empresa_id)
    if not apt:
        return None, ["Apartamento no encontrado."]

    try:
        clean = _update_schema.load(json_data)
    except ValidationError as exc:
        return None, _flatten(exc.messages)

    repo.update(apt, **clean)
    db.session.commit()
    return _apt_to_dict(apt), []


def delete_apartamento(empresa_id: str, apartamento_id: str) -> str | None:
    apt = repo.get_by_id(apartamento_id, empresa_id)
    if not apt:
        return "Apartamento no encontrado."
    repo.soft_delete(apt)
    db.session.commit()
    return None


# ── Sincronización con Smoobu ────────────────────────────────────────────


def sync_from_smoobu(empresa_id: str) -> tuple[dict | None, str | None]:
    config = repo.get_pms_config(empresa_id)
    if not config or not config.api_key_cifrada:
        return None, "No hay configuración PMS. Guarda tu API key primero."

    if config.proveedor != "smoobu":
        return None, f"El proveedor configurado es '{config.proveedor}', no 'smoobu'."

    api_key = decrypt(config.api_key_cifrada)
    if api_key is None:
        return None, "No se pudo descifrar la API key. Vuelve a configurarla."

    client = SmoobuClient(api_key)
    try:
        apartments = client.fetch_all_normalized()
    except requests.RequestException as exc:
        logger.error("Error al conectar con Smoobu: %s", exc)
        repo.create_sync_log(
            empresa_id=empresa_id,
            origen="pms",
            estado="error",
            detalle=f"Error de conexión con Smoobu: {exc}",
        )
        db.session.commit()
        return None, f"Error al conectar con Smoobu: {exc}"

    nuevos = 0
    actualizados = 0
    for apt_data in apartments:
        _, es_nuevo = repo.upsert_from_external(
            empresa_id=empresa_id,
            id_externo=apt_data.id_externo,
            nombre=apt_data.nombre,
            direccion=apt_data.direccion,
            ciudad=apt_data.ciudad,
            pms_origen=ORIGEN_SMOOBU,
        )
        if es_nuevo:
            nuevos += 1
        else:
            actualizados += 1

    repo.create_sync_log(
        empresa_id=empresa_id,
        origen="pms",
        estado="exito",
        num_registros=len(apartments),
        detalle=f"Smoobu: {nuevos} nuevos, {actualizados} actualizados",
    )
    db.session.commit()

    return {
        "total": len(apartments),
        "nuevos": nuevos,
        "actualizados": actualizados,
    }, None


# ── Importación XLSX ─────────────────────────────────────────────────────


def import_from_xlsx(empresa_id: str, file_bytes: bytes) -> tuple[dict | None, list[str]]:
    apartments, parse_errors = parse_xlsx(file_bytes)

    if not apartments and parse_errors:
        repo.create_sync_log(
            empresa_id=empresa_id,
            origen="xlsx",
            estado="error",
            detalle="; ".join(parse_errors),
        )
        db.session.commit()
        return None, parse_errors

    nuevos = 0
    actualizados = 0
    for apt_data in apartments:
        _, es_nuevo = repo.upsert_from_external(
            empresa_id=empresa_id,
            id_externo=apt_data.id_externo,
            nombre=apt_data.nombre,
            direccion=apt_data.direccion,
            ciudad=apt_data.ciudad,
            pms_origen=ORIGEN_XLSX,
        )
        if es_nuevo:
            nuevos += 1
        else:
            actualizados += 1

    estado = "parcial" if parse_errors else "exito"
    repo.create_sync_log(
        empresa_id=empresa_id,
        origen="xlsx",
        estado=estado,
        num_registros=len(apartments),
        detalle=f"XLSX: {nuevos} nuevos, {actualizados} actualizados"
        + (f" ({len(parse_errors)} errores)" if parse_errors else ""),
    )
    db.session.commit()

    return {
        "total": len(apartments),
        "nuevos": nuevos,
        "actualizados": actualizados,
    }, parse_errors


# ── Preview importación XLSX ─────────────────────────────────────────────


def preview_import_xlsx(empresa_id: str, file_bytes: bytes) -> tuple[dict, list[str]]:
    apartments, parse_errors = parse_xlsx(file_bytes)

    nuevos = []
    actualizados = []
    sin_cambios = []

    for apt_data in apartments:
        existing = repo.get_by_id_externo(empresa_id, apt_data.id_externo)
        if not existing:
            nuevos.append({
                "id_externo": apt_data.id_externo,
                "nombre": apt_data.nombre,
                "ciudad": apt_data.ciudad,
                "direccion": apt_data.direccion,
            })
        else:
            campos_cambian = (
                existing.nombre != apt_data.nombre
                or (apt_data.ciudad and existing.ciudad != apt_data.ciudad)
                or (apt_data.direccion and existing.direccion != apt_data.direccion)
            )
            entry = {
                "id_externo": apt_data.id_externo,
                "nombre": apt_data.nombre,
                "nombre_actual": existing.nombre,
                "ciudad": apt_data.ciudad,
                "direccion": apt_data.direccion,
            }
            if campos_cambian:
                actualizados.append(entry)
            else:
                sin_cambios.append(entry)

    return {
        "nuevos": nuevos,
        "actualizados": actualizados,
        "sin_cambios": sin_cambios,
        "errores": parse_errors,
    }, []


# ── Configuración PMS ────────────────────────────────────────────────────


def save_pms_config(empresa_id: str, json_data: dict) -> tuple[dict | None, list[str]]:
    try:
        clean = _pms_config_schema.load(json_data)
    except ValidationError as exc:
        return None, _flatten(exc.messages)

    api_key_cifrada = encrypt(clean["api_key"])
    config = repo.upsert_pms_config(
        empresa_id=empresa_id,
        proveedor=clean["proveedor"],
        api_key_cifrada=api_key_cifrada,
        endpoint=clean.get("endpoint"),
    )
    db.session.commit()

    return {
        "proveedor": config.proveedor,
        "endpoint": config.endpoint,
        "activo": config.activo,
        "ultimo_sync": config.ultimo_sync.isoformat() if config.ultimo_sync else None,
    }, []


def get_pms_config(empresa_id: str) -> dict | None:
    config = repo.get_pms_config(empresa_id)
    if not config:
        return None
    return {
        "proveedor": config.proveedor,
        "endpoint": config.endpoint,
        "activo": config.activo,
        "ultimo_sync": config.ultimo_sync.isoformat() if config.ultimo_sync else None,
    }


def delete_pms_config(empresa_id: str) -> str | None:
    config = repo.get_pms_config(empresa_id)
    if not config:
        return "No hay configuración PMS para eliminar."
    repo.delete_pms_config(config)
    db.session.commit()
    return None


# ── Utilidades ───────────────────────────────────────────────────────────


def _flatten(messages: dict) -> list[str]:
    errors: list[str] = []
    for field, msgs in messages.items():
        if isinstance(msgs, list):
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        elif isinstance(msgs, dict):
            for sub_msgs in msgs.values():
                if isinstance(sub_msgs, list):
                    errors.extend(f"{field}: {m}" for m in sub_msgs)
    return errors
