"""Blueprint de notificaciones para check-in tardíos.

Rutas (todas requieren JWT):
- GET  /api/notificaciones/checkin-tardio/status     → estado PMS, check-ins hoy, apartamentos, hora_corte
- POST /api/notificaciones/checkin-tardio/checkins   → parsea XLSX, devuelve check-ins tardíos; en memoria, no persiste — RGPD
- GET  /api/notificaciones/checkin-tardio/plantillas → lista plantillas de categoría 'checkin_tardio'
- POST /api/notificaciones/checkin-tardio/plantillas → crea plantilla de categoría 'checkin_tardio'
"""

import logging
import uuid

from flask import Blueprint, g, jsonify, request

from app.extensions import db, limiter
from app.perfil import repository as perfil_repo
from app.security.jwt import jwt_required
from app.h_notificaciones_tardias import service
from app.h_vault_comunicaciones.model import PlantillaVault

logger = logging.getLogger(__name__)

notificaciones_bp = Blueprint("notificaciones", __name__)

_CATEGORIA = "checkin_tardio"


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


# ── Status ────────────────────────────────────────────────────────────────


@notificaciones_bp.route("/api/notificaciones/checkin-tardio/status", methods=["GET"])
@jwt_required
def get_status():
    data = service.get_status(_empresa_id())
    return jsonify({"ok": True, **data}), 200


# ── XLSX ──────────────────────────────────────────────────────────────────


@notificaciones_bp.route("/api/notificaciones/checkin-tardio/checkins", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def upload_xlsx():
    if "file" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba un campo 'file' con el archivo."]}), 400

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo debe tener extensión .xlsx."]}), 400

    file_bytes = f.read()
    if not file_bytes:
        return jsonify({"ok": False, "errors": ["El archivo está vacío."]}), 400

    config = perfil_repo.get_notif_tardio_config(_empresa_id())
    hora_corte = config.get("hora_corte", "20:00")

    checkins, advertencias = service.parse_checkins_xlsx(
        file_bytes, _empresa_id(), hora_corte, config
    )

    result: dict = {"ok": True, "checkins": checkins}
    if advertencias:
        result["warnings"] = advertencias
    return jsonify(result), 200


# ── Plantillas ────────────────────────────────────────────────────────────


def _plantilla_to_dict(p: PlantillaVault) -> dict:
    return {"id": str(p.id), "nombre": p.nombre, "contenido": p.contenido}


@notificaciones_bp.route("/api/notificaciones/checkin-tardio/plantillas", methods=["GET"])
@jwt_required
def list_plantillas():
    plantillas = (
        PlantillaVault.query
        .filter_by(empresa_id=_empresa_id(), categoria=_CATEGORIA, activa=True)
        .order_by(PlantillaVault.created_at.asc())
        .all()
    )
    return jsonify({"ok": True, "plantillas": [_plantilla_to_dict(p) for p in plantillas]}), 200


@notificaciones_bp.route("/api/notificaciones/checkin-tardio/plantillas", methods=["POST"])
@jwt_required
def create_plantilla():
    body = request.get_json(silent=True) or {}
    nombre = (body.get("nombre") or "").strip()
    contenido = (body.get("contenido") or "").strip()

    if not nombre:
        return jsonify({"ok": False, "errors": ["El nombre es obligatorio."]}), 400
    if not contenido:
        return jsonify({"ok": False, "errors": ["El contenido es obligatorio."]}), 400

    plantilla = PlantillaVault(
        id=uuid.uuid4(),
        empresa_id=_empresa_id(),
        nombre=nombre,
        contenido=contenido,
        categoria=_CATEGORIA,
        idioma="es",
    )
    db.session.add(plantilla)
    db.session.commit()

    return jsonify({"ok": True, "plantilla": _plantilla_to_dict(plantilla)}), 201
