"""Blueprint de apartamentos — CRUD, sync Smoobu e importación XLSX.

Rutas (todas requieren JWT):
- GET    /api/apartamentos              → listar
- GET    /api/apartamentos/<id>         → detalle
- POST   /api/apartamentos              → alta manual
- PUT    /api/apartamentos/<id>         → actualizar
- DELETE /api/apartamentos/<id>         → soft delete
- POST   /api/apartamentos/sync/smoobu  → sincronizar desde Smoobu
- POST   /api/apartamentos/import/xlsx  → importar desde Excel
- GET    /api/pms/config                → ver configuración PMS
- POST   /api/pms/config                → guardar configuración PMS
- DELETE /api/pms/config                → eliminar configuración PMS
"""

import logging

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import limiter
from app.security.jwt import jwt_required
from app.apartamentos import service

logger = logging.getLogger(__name__)

apartamentos_bp = Blueprint("apartamentos", __name__)


def _empresa_id() -> str:
    """Extrae el empresa_id del JWT (claim 'empresa_id' del token)."""
    return g.jwt_claims["empresa_id"]


# ── CRUD ─────────────────────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos", methods=["GET"])
@jwt_required
def list_apartamentos():
    """Lista todos los apartamentos activos de la empresa."""
    data = service.list_apartamentos(_empresa_id())
    return jsonify({"ok": True, "apartamentos": data}), 200


@apartamentos_bp.route("/api/apartamentos/<apartamento_id>", methods=["GET"])
@jwt_required
def get_apartamento(apartamento_id: str):
    """Detalle de un apartamento."""
    data, error = service.get_apartamento(_empresa_id(), apartamento_id)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True, "apartamento": data}), 200


@apartamentos_bp.route("/api/apartamentos", methods=["POST"])
@jwt_required
def create_apartamento():
    """Alta manual de un apartamento."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.create_apartamento(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "apartamento": data}), 201


@apartamentos_bp.route("/api/apartamentos/<apartamento_id>", methods=["PUT"])
@jwt_required
def update_apartamento(apartamento_id: str):
    """Actualiza un apartamento."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.update_apartamento(_empresa_id(), apartamento_id, json_data)
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True, "apartamento": data}), 200


@apartamentos_bp.route("/api/apartamentos/<apartamento_id>", methods=["DELETE"])
@jwt_required
def delete_apartamento(apartamento_id: str):
    """Soft-delete de un apartamento."""
    error = service.delete_apartamento(_empresa_id(), apartamento_id)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200


# ── Sincronización Smoobu ────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/sync/smoobu", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def sync_smoobu():
    """Sincroniza apartamentos desde la API de Smoobu."""
    data, error = service.sync_from_smoobu(_empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "resultado": data}), 200


# ── Importación XLSX ─────────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/import/xlsx", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def import_xlsx():
    """Importa apartamentos desde un archivo Excel (.xlsx)."""
    if "file" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba un archivo 'file'."]}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo debe ser .xlsx."]}), 400

    max_bytes = current_app.config.get("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    content_length = request.content_length
    if content_length is not None and content_length > max_bytes:
        return jsonify({"ok": False, "errors": ["El archivo supera el tamaño máximo permitido."]}), 413

    file_bytes = file.read()
    if not file_bytes:
        return jsonify({"ok": False, "errors": ["El archivo está vacío."]}), 400

    data, errors = service.import_from_xlsx(_empresa_id(), file_bytes)

    if data is None:
        return jsonify({"ok": False, "errors": errors}), 422

    result = {"ok": True, "resultado": data}
    if errors:
        result["warnings"] = errors
    return jsonify(result), 200


# ── Configuración PMS ────────────────────────────────────────────────────


@apartamentos_bp.route("/api/pms/config", methods=["GET"])
@jwt_required
def get_pms_config():
    """Devuelve la configuración PMS de la empresa (sin la API key)."""
    data = service.get_pms_config(_empresa_id())
    if data is None:
        return jsonify({"ok": True, "config": None}), 200
    return jsonify({"ok": True, "config": data}), 200


@apartamentos_bp.route("/api/pms/config", methods=["POST"])
@jwt_required
def save_pms_config():
    """Guarda o actualiza la configuración PMS (API key cifrada)."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_pms_config(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "config": data}), 200


@apartamentos_bp.route("/api/pms/config", methods=["DELETE"])
@jwt_required
def delete_pms_config():
    """Elimina la configuración PMS de la empresa."""
    error = service.delete_pms_config(_empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200
