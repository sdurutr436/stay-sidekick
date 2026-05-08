"""Blueprint del módulo de empresas.

Rutas:
- GET /api/empresas → lista todas las empresas (solo superadmin)
"""

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.empresas.model import Empresa
from app.empresas.repository import crear_empresa
from app.empresas.schemas import CrearEmpresaSchema
from app.security.jwt import jwt_required

empresas_bp = Blueprint("empresas", __name__)


@empresas_bp.route("/api/empresas", methods=["GET"])
@jwt_required
def list_empresas():
    if not g.jwt_claims.get("es_superadmin"):
        return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
    filas = (
        Empresa.query
        .with_entities(Empresa.id, Empresa.nombre, Empresa.email)
        .filter_by(activa=True)
        .order_by(Empresa.nombre)
        .all()
    )
    return jsonify({
        "ok": True,
        "empresas": [{"id": str(f.id), "nombre": f.nombre, "email": f.email} for f in filas],
    }), 200


@empresas_bp.route("/api/empresas", methods=["POST"])
@jwt_required
def crear_empresa_route():
    if not g.jwt_claims.get("es_superadmin"):
        return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
    schema = CrearEmpresaSchema()
    errors = schema.validate(request.json or {})
    if errors:
        msgs = [msg for lista in errors.values() for msg in lista]
        return jsonify({"ok": False, "errors": msgs}), 422
    data = schema.load(request.json)
    try:
        empresa = crear_empresa(data["nombre"], data["email"])
    except IntegrityError:
        return jsonify({"ok": False, "errors": ["Ya existe una empresa con ese email."]}), 409
    return jsonify({"ok": True, "empresa": {"id": str(empresa.id), "nombre": empresa.nombre, "email": empresa.email}}), 201
