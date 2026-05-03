"""Blueprint de notificaciones para check-in tardíos.

Rutas (todas requieren JWT):
- GET  /api/notificaciones/checkin-tardio/status   → estado: Gmail, PMS, check-ins hoy, apartamentos, hora_corte
- POST /api/notificaciones/checkin-tardio/checkins → parsea XLSX, devuelve check-ins tardíos (hora_llegada >= hora_corte); en memoria, no persiste — RGPD
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.extensions import limiter
from app.perfil import repository as perfil_repo
from app.security.jwt import jwt_required
from app.h_notificaciones_tardias import service

logger = logging.getLogger(__name__)

notificaciones_bp = Blueprint("notificaciones", __name__)


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


# TODO: Gmail API OAuth -- pendiente de implementar (scope futuro)
