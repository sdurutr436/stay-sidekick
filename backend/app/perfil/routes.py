"""Blueprint de perfil de usuario.

Rutas (todas requieren JWT):
- GET  /api/perfil                          → datos del usuario autenticado
- PUT  /api/perfil/password                 → cambiar contraseña
- GET  /api/perfil/integraciones            → estado de las integraciones de la empresa
- PUT  /api/perfil/integraciones/pms        → actualizar integración PMS (solo admin)
- PUT  /api/perfil/integraciones/ia         → actualizar integración IA (solo admin)
- GET  /api/perfil/xlsx-apartamentos        → leer configuración de columnas XLSX
- PUT  /api/perfil/xlsx-apartamentos        → guardar configuración de columnas XLSX (solo admin)
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.security.jwt import jwt_required
from app.perfil import service

logger = logging.getLogger(__name__)

perfil_bp = Blueprint("perfil", __name__)


def _user_id() -> str:
    return g.jwt_claims["user_id"]


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


def _is_admin() -> bool:
    return g.jwt_claims.get("rol") == "admin"


@perfil_bp.route("/api/perfil", methods=["GET"])
@jwt_required
def get_perfil():
    data = service.get_perfil(_user_id())
    if not data:
        return jsonify({"ok": False, "errors": ["Usuario no encontrado."]}), 404
    return jsonify({"ok": True, "data": data}), 200


@perfil_bp.route("/api/perfil/password", methods=["PUT"])
@jwt_required
def cambiar_password():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    errors = service.cambiar_password(_user_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True}), 200


@perfil_bp.route("/api/perfil/integraciones", methods=["GET"])
@jwt_required
def get_integraciones():
    data = service.get_integraciones(_empresa_id())
    return jsonify({"ok": True, "data": data}), 200


@perfil_bp.route("/api/perfil/integraciones/pms", methods=["PUT"])
@jwt_required
def actualizar_pms():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede modificar las integraciones."]}), 403

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    errors = service.actualizar_pms(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True}), 200


@perfil_bp.route("/api/perfil/integraciones/ia", methods=["PUT"])
@jwt_required
def actualizar_ia():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede modificar las integraciones."]}), 403

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    errors = service.actualizar_ia(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True}), 200


@perfil_bp.route("/api/perfil/xlsx-apartamentos", methods=["GET"])
@jwt_required
def get_xlsx_apartamentos():
    config = service.get_xlsx_apartamentos_config(_empresa_id())
    return jsonify({"ok": True, "config": config or None}), 200


@perfil_bp.route("/api/perfil/xlsx-apartamentos", methods=["PUT"])
@jwt_required
def save_xlsx_apartamentos():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede modificar esta configuración."]}), 403

    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    errors = service.save_xlsx_apartamentos_config(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True}), 200
