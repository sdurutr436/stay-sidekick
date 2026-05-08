"""Blueprint de usuarios — CRUD de usuarios de empresa.

Rutas (todas requieren JWT con rol=admin):
- GET    /api/usuarios                          → lista usuarios de la empresa
- POST   /api/usuarios                          → crear usuario (email, rol)
- DELETE /api/usuarios/<id>                     → borrar usuario
- PATCH  /api/usuarios/<id>                     → editar rol
- PATCH  /api/usuarios/<id>/resetear-password   → nueva contraseña temporal
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.security.jwt import jwt_required
from app.usuarios import service
from app.usuarios.model import ROL_ADMIN

logger = logging.getLogger(__name__)

usuarios_bp = Blueprint("usuarios", __name__)


def _claims():
    return g.jwt_claims


def _solo_admin():
    if _claims().get("rol") != ROL_ADMIN:
        return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
    return None


# ── Listar ────────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios", methods=["GET"])
@jwt_required
def list_usuarios():
    err = _solo_admin()
    if err:
        return err
    data = service.listar_usuarios(_claims()["empresa_id"])
    return jsonify({"ok": True, **data}), 200


# ── Crear ─────────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios", methods=["POST"])
@jwt_required
def create_usuario():
    err = _solo_admin()
    if err:
        return err
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400
    result, errors = service.crear_usuario(_claims()["empresa_id"], json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, **result}), 201


# ── Eliminar ──────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@jwt_required
def delete_usuario(usuario_id: str):
    err = _solo_admin()
    if err:
        return err
    claims = _claims()
    errors = service.eliminar_usuario(claims["empresa_id"], usuario_id, claims["user_id"])
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True}), 200


# ── Editar rol ────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>", methods=["PATCH"])
@jwt_required
def patch_usuario(usuario_id: str):
    err = _solo_admin()
    if err:
        return err
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400
    data, errors = service.editar_rol(_claims()["empresa_id"], usuario_id, json_data)
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True, "usuario": data}), 200


# ── Resetear contraseña ───────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>/resetear-password", methods=["PATCH"])
@jwt_required
def resetear_password(usuario_id: str):
    err = _solo_admin()
    if err:
        return err
    data, errors = service.resetear_password(_claims()["empresa_id"], usuario_id)
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True, **data}), 200
