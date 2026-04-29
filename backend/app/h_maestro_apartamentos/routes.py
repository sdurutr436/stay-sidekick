"""Blueprint de apartamentos — CRUD, sincronización Smoobu e importación XLSX.

Rutas (todas requieren JWT):
- GET    /api/apartamentos                      → listar apartamentos activos de la empresa
- GET    /api/apartamentos/<id>                 → detalle de un apartamento
- POST   /api/apartamentos                      → alta manual de apartamento
- PUT    /api/apartamentos/<id>                 → actualizar campos de un apartamento
- DELETE /api/apartamentos/<id>                 → soft delete (marca como inactivo)
- POST   /api/apartamentos/sincronizacion/smoobu → [acción] pull de propiedades desde Smoobu API (upsert interno)
- POST   /api/apartamentos/importacion          → [acción] importa apartamentos desde XLSX subido (multipart, upsert interno)
- GET    /api/apartamentos/pms                  → lee configuración del PMS activo (sin exponer API key)
- PUT    /api/apartamentos/pms                  → crea o actualiza configuración PMS (upsert idempotente → PUT)
- DELETE /api/apartamentos/pms                  → elimina configuración PMS
"""

import logging

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import limiter
from app.security.jwt import jwt_required
from app.h_maestro_apartamentos import service

logger = logging.getLogger(__name__)

apartamentos_bp = Blueprint("apartamentos", __name__)


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


# ── CRUD ─────────────────────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos", methods=["GET"])
@jwt_required
def list_apartamentos():
    data = service.list_apartamentos(_empresa_id())
    return jsonify({"ok": True, "apartamentos": data}), 200


@apartamentos_bp.route("/api/apartamentos/<apartamento_id>", methods=["GET"])
@jwt_required
def get_apartamento(apartamento_id: str):
    data, error = service.get_apartamento(_empresa_id(), apartamento_id)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True, "apartamento": data}), 200


@apartamentos_bp.route("/api/apartamentos", methods=["POST"])
@jwt_required
def create_apartamento():
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
    error = service.delete_apartamento(_empresa_id(), apartamento_id)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200


# ── Sincronización Smoobu ────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/sincronizacion/smoobu", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def sync_smoobu():
    data, error = service.sync_from_smoobu(_empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "resultado": data}), 200


# ── Importación XLSX ─────────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/importacion", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def import_xlsx():
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


# ── Preview importación XLSX ─────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/importacion/preview", methods=["POST"])
@limiter.limit("30/hour")
@jwt_required
def preview_import_xlsx():
    if "file" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba un archivo 'file'."]}), 400

    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo debe ser .xlsx."]}), 400

    file_bytes = file.read()
    if not file_bytes:
        return jsonify({"ok": False, "errors": ["El archivo está vacío."]}), 400

    data, errors = service.preview_import_xlsx(_empresa_id(), file_bytes)
    if data is None:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True, "preview": data}), 200


# ── Configuración PMS ────────────────────────────────────────────────────


@apartamentos_bp.route("/api/apartamentos/pms", methods=["GET"])
@jwt_required
def get_pms_config():
    data = service.get_pms_config(_empresa_id())
    if data is None:
        return jsonify({"ok": True, "config": None}), 200
    return jsonify({"ok": True, "config": data}), 200


@apartamentos_bp.route("/api/apartamentos/pms", methods=["PUT"])
@jwt_required
def save_pms_config():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_pms_config(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "config": data}), 200


@apartamentos_bp.route("/api/apartamentos/pms", methods=["DELETE"])
@jwt_required
def delete_pms_config():
    error = service.delete_pms_config(_empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200
