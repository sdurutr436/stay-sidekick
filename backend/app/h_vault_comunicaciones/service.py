"""Servicio del Vault de comunicaciones."""

from app.h_vault_comunicaciones import repository
from app.h_vault_comunicaciones.model import PlantillaVault


def _to_dict(p: PlantillaVault) -> dict:
    return {
        "id": str(p.id),
        "nombre": p.nombre,
        "contenido": p.contenido,
        "idioma": p.idioma,
        "categoria": p.categoria,
        "activa": p.activa,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


def list_plantillas(empresa_id: str, categoria: str | None, idioma: str | None) -> list[dict]:
    return [_to_dict(p) for p in repository.list_plantillas(empresa_id, categoria, idioma)]


def get_plantilla(plantilla_id: str, empresa_id: str) -> dict | None:
    p = repository.get_plantilla(plantilla_id, empresa_id)
    return _to_dict(p) if p else None


def crear_plantilla(empresa_id: str, data: dict) -> dict:
    return _to_dict(repository.crear_plantilla(empresa_id, data))


def actualizar_plantilla(
    plantilla_id: str, empresa_id: str, data: dict
) -> tuple[dict | None, str | None]:
    p = repository.actualizar_plantilla(plantilla_id, empresa_id, data)
    if p is None:
        return None, "Plantilla no encontrada."
    return _to_dict(p), None


def eliminar_plantilla(plantilla_id: str, empresa_id: str) -> str | None:
    ok = repository.soft_delete_plantilla(plantilla_id, empresa_id)
    return None if ok else "Plantilla no encontrada."
