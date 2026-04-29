"""Blueprint de notificaciones para check-in tardíos.

Rutas (todas requieren JWT):
- GET  /api/notificaciones/checkin-tardio/status   → estado: Gmail, PMS, check-ins hoy, apartamentos
- POST /api/notificaciones/checkin-tardio/checkins → parsea XLSX subido, devuelve check-ins de hoy (en memoria, no persiste — RGPD)
- POST /api/notificaciones/checkin-tardio/email    → dispara envío de email de notificación (destinatario + mensaje)
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.extensions import limiter
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

    checkins, advertencias = service.parse_checkins_xlsx(file_bytes)

    result: dict = {"ok": True, "checkins": checkins}
    if advertencias:
        result["warnings"] = advertencias
    return jsonify(result), 200


# ── Envío de notificación ─────────────────────────────────────────────────


@notificaciones_bp.route("/api/notificaciones/checkin-tardio/email", methods=["POST"])
@limiter.limit("30/hour")
@jwt_required
def enviar_notificacion():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    destinatario = (json_data.get("destinatario") or "").strip()
    asunto = (json_data.get("asunto") or "Recordatorio de check-in").strip()
    mensaje = (json_data.get("mensaje") or "").strip()

    if not destinatario:
        return jsonify({"ok": False, "errors": ["El campo 'destinatario' es obligatorio."]}), 422
    if not mensaje:
        return jsonify({"ok": False, "errors": ["El campo 'mensaje' no puede estar vacío."]}), 422

    ok, error = service.enviar_notificacion(destinatario, asunto, mensaje)
    if not ok:
        return jsonify({"ok": False, "errors": [error]}), 400

    return jsonify({"ok": True}), 200
