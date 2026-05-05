"""Repositorio de datos del Vault de comunicaciones."""

from app.extensions import db
from app.h_vault_comunicaciones.model import PlantillaVault


def list_plantillas(
    empresa_id: str,
    categoria: str | None,
    idioma: str | None,
) -> list[PlantillaVault]:
    q = PlantillaVault.query.filter_by(empresa_id=empresa_id, activa=True)
    if categoria is not None:
        q = q.filter_by(categoria=categoria)
    if idioma is not None:
        q = q.filter_by(idioma=idioma)
    return q.order_by(PlantillaVault.updated_at.desc()).all()


def get_plantilla(plantilla_id: str, empresa_id: str) -> PlantillaVault | None:
    return PlantillaVault.query.filter_by(
        id=plantilla_id, empresa_id=empresa_id, activa=True
    ).first()


def crear_plantilla(empresa_id: str, data: dict) -> PlantillaVault:
    p = PlantillaVault(
        empresa_id=empresa_id,
        nombre=data["nombre"],
        contenido=data["contenido"],
        idioma=data["idioma"],
        categoria=data.get("categoria"),
    )
    db.session.add(p)
    db.session.commit()
    return p


def actualizar_plantilla(
    plantilla_id: str, empresa_id: str, data: dict
) -> PlantillaVault | None:
    p = get_plantilla(plantilla_id, empresa_id)
    if p is None:
        return None
    p.nombre = data["nombre"]
    p.contenido = data["contenido"]
    if data.get("idioma") is not None:
        p.idioma = data["idioma"]
    if "categoria" in data:
        p.categoria = data["categoria"]
    db.session.commit()
    return p


def soft_delete_plantilla(plantilla_id: str, empresa_id: str) -> bool:
    p = PlantillaVault.query.filter_by(id=plantilla_id, empresa_id=empresa_id).first()
    if p is None:
        return False
    p.activa = False
    db.session.commit()
    return True
