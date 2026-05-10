"""Blueprint de usuarios — CRUD de usuarios de empresa.

Rutas (todas requieren JWT con rol=admin o es_superadmin):
- GET    /api/usuarios                          → lista usuarios de la empresa
- POST   /api/usuarios                          → crear usuario (email, rol)
- DELETE /api/usuarios/<id>                     → borrar usuario
- PATCH  /api/usuarios/<id>                     → editar rol
- PATCH  /api/usuarios/<id>/contrasena           → nueva contraseña temporal

Superadmin: puede añadir ?empresa_id=<uuid> en cualquier ruta para operar
sobre cualquier empresa.
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.security.require_rol import require_rol
from app.usuarios import service
from app.usuarios.schemas import UsuarioResponseSchema

logger = logging.getLogger(__name__)

usuarios_bp = Blueprint("usuarios", __name__)

_usuario_response = UsuarioResponseSchema()
_usuarios_response = UsuarioResponseSchema(many=True)


def _empresa_id_efectiva():
    """Empresa sobre la que operar: ?empresa_id para superadmin, JWT para el resto."""
    claims = g.jwt_claims
    if claims.get("es_superadmin"):
        return request.args.get("empresa_id") or claims["empresa_id"]
    return claims["empresa_id"]


# ── Listar ────────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios", methods=["GET"])
@require_rol("admin", "superadmin")
def list_usuarios():
    data = service.listar_usuarios(_empresa_id_efectiva())
    return jsonify({
        "ok": True,
        "usuarios": _usuarios_response.dump(data["usuarios"]),
        "max_usuarios": data["max_usuarios"],
    }), 200


# ── Crear ─────────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios", methods=["POST"])
@require_rol("admin", "superadmin")
def create_usuario():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400
    result, errors = service.crear_usuario(_empresa_id_efectiva(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({
        "ok": True,
        "usuario": _usuario_response.dump(result["usuario"]),
        "password_temporal": result["password_temporal"],
    }), 201


# ── Eliminar ──────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>", methods=["DELETE"])
@require_rol("admin", "superadmin")
def delete_usuario(usuario_id: str):
    claims = g.jwt_claims
    errors = service.eliminar_usuario(_empresa_id_efectiva(), usuario_id, claims["user_id"])
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True}), 200


# ── Editar rol ────────────────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>", methods=["PATCH"])
@require_rol("admin", "superadmin")
def patch_usuario(usuario_id: str):
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400
    data, errors = service.editar_rol(_empresa_id_efectiva(), usuario_id, json_data)
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True, "usuario": _usuario_response.dump(data)}), 200


# ── Resetear contraseña ───────────────────────────────────────────────────


@usuarios_bp.route("/api/usuarios/<usuario_id>/contrasena", methods=["PATCH"])
@require_rol("admin", "superadmin")
def resetear_password(usuario_id: str):
    data, errors = service.resetear_password(_empresa_id_efectiva(), usuario_id)
    if errors:
        status = 404 if "no encontrado" in errors[0].lower() else 422
        return jsonify({"ok": False, "errors": errors}), status
    return jsonify({"ok": True, **data}), 200
