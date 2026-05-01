"""Blueprint del mapa de calor.

Rutas (todas requieren JWT):
- GET  /api/heatmap                → genera mapa de calor desde PMS
- POST /api/heatmap/xlsx           → genera mapa de calor desde XLSX
- GET  /api/heatmap/umbrales       → lee umbrales de intensidad
- PUT  /api/heatmap/umbrales       → guarda umbrales (solo admin)
- GET  /api/heatmap/config-xlsx    → lee configuración de columnas XLSX
- PUT  /api/heatmap/config-xlsx    → guarda configuración de columnas (solo admin)
"""

import logging
from datetime import date

from flask import Blueprint, g, jsonify, request

from app.extensions import limiter
from app.security.jwt import jwt_required
from app.h_mapa_de_calor import service

logger = logging.getLogger(__name__)

heatmap_bp = Blueprint("heatmap", __name__)


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


def _is_admin() -> bool:
    return g.jwt_claims.get("rol") == "admin"


def _parse_date(value: str | None, campo: str) -> tuple[date | None, str | None]:
    """Parsea una fecha ISO desde query string. Devuelve (date, None) o (None, error)."""
    if not value:
        return None, f"El parámetro '{campo}' es obligatorio."
    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, f"'{campo}' no es una fecha válida (formato esperado: YYYY-MM-DD)."


# ── Umbrales ──────────────────────────────────────────────────────────────


@heatmap_bp.route("/api/heatmap/umbrales", methods=["GET"])
@jwt_required
def get_umbrales():
    umbrales = service.get_umbrales(_empresa_id())
    return jsonify({"ok": True, "umbrales": umbrales}), 200


@heatmap_bp.route("/api/heatmap/umbrales", methods=["PUT"])
@jwt_required
def save_umbrales():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Acceso restringido a administradores."]}), 403

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_umbrales(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "umbrales": data}), 200


# ── Configuración XLSX ────────────────────────────────────────────────────


@heatmap_bp.route("/api/heatmap/config-xlsx", methods=["GET"])
@jwt_required
def get_config_xlsx():
    cfg = service.get_config_xlsx(_empresa_id())
    return jsonify({"ok": True, "config": cfg}), 200


@heatmap_bp.route("/api/heatmap/config-xlsx", methods=["PUT"])
@jwt_required
def save_config_xlsx():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Acceso restringido a administradores."]}), 403

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_config_xlsx(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "config": data}), 200


# ── Generación desde PMS ──────────────────────────────────────────────────


@heatmap_bp.route("/api/heatmap", methods=["GET"])
@jwt_required
def generar_desde_pms():
    desde_str = request.args.get("desde")
    hasta_str = request.args.get("hasta")

    desde, err = _parse_date(desde_str, "desde")
    if err:
        return jsonify({"ok": False, "errors": [err]}), 422
    hasta, err = _parse_date(hasta_str, "hasta")
    if err:
        return jsonify({"ok": False, "errors": [err]}), 422

    if desde > hasta:
        return jsonify({"ok": False, "errors": ["'desde' debe ser anterior o igual a 'hasta'."]}), 422

    if desde < date.today():
        return jsonify({
            "ok": False,
            "errors": ["No se puede generar un mapa de calor con fechas pasadas."],
        }), 422

    dias, error = service.generar_desde_pms(_empresa_id(), desde, hasta)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "dias": dias}), 200


# ── Generación desde XLSX ─────────────────────────────────────────────────


@heatmap_bp.route("/api/heatmap/xlsx", methods=["POST"])
@limiter.limit("30/hour")
@jwt_required
def generar_desde_xlsx():
    if "checkins" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba el campo 'checkins' con un archivo .xlsx."]}), 400

    desde_str = request.form.get("desde")
    hasta_str = request.form.get("hasta")

    desde, err = _parse_date(desde_str, "desde")
    if err:
        return jsonify({"ok": False, "errors": [err]}), 422
    hasta, err = _parse_date(hasta_str, "hasta")
    if err:
        return jsonify({"ok": False, "errors": [err]}), 422

    if desde > hasta:
        return jsonify({"ok": False, "errors": ["'desde' debe ser anterior o igual a 'hasta'."]}), 422

    if desde < date.today():
        return jsonify({
            "ok": False,
            "errors": ["No se puede generar un mapa de calor con fechas pasadas."],
        }), 422

    checkins_file = request.files["checkins"]
    if not checkins_file.filename or not checkins_file.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo 'checkins' debe ser .xlsx."]}), 400

    checkins_bytes = checkins_file.read()
    if not checkins_bytes:
        return jsonify({"ok": False, "errors": ["El archivo 'checkins' está vacío."]}), 400

    checkouts_bytes: bytes | None = None
    if "checkouts" in request.files:
        checkouts_file = request.files["checkouts"]
        if checkouts_file.filename:
            if not checkouts_file.filename.lower().endswith(".xlsx"):
                return jsonify({"ok": False, "errors": ["El archivo 'checkouts' debe ser .xlsx."]}), 400
            checkouts_bytes = checkouts_file.read()
            if not checkouts_bytes:
                return jsonify({"ok": False, "errors": ["El archivo 'checkouts' está vacío."]}), 400

    dias, warnings, error = service.generar_desde_xlsx(
        _empresa_id(), checkins_bytes, checkouts_bytes, desde, hasta
    )
    if error:
        return jsonify({"ok": False, "errors": [error]}), 422

    result: dict = {"ok": True, "dias": dias}
    if warnings:
        result["warnings"] = warnings
    return jsonify(result), 200
