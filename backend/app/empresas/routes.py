"""Blueprint del módulo de empresas.

Rutas:
- GET /api/empresas → lista todas las empresas (solo superadmin)
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.empresas.model import Empresa
from app.empresas.repository import crear_empresa
from app.empresas.schemas import CrearEmpresaSchema, EmpresaResponseSchema
from app.security.require_rol import require_rol

empresas_bp = Blueprint("empresas", __name__)

_empresa_response = EmpresaResponseSchema()
_empresas_response = EmpresaResponseSchema(many=True)


@empresas_bp.route("/api/empresas", methods=["GET"])
@require_rol("superadmin")
def list_empresas():
    filas = (
        Empresa.query
        .with_entities(Empresa.id, Empresa.nombre, Empresa.email)
        .filter_by(activa=True)
        .order_by(Empresa.nombre)
        .all()
    )
    return jsonify({"ok": True, "empresas": _empresas_response.dump(filas)}), 200


@empresas_bp.route("/api/empresas", methods=["POST"])
@require_rol("superadmin")
def crear_empresa_route():
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
    return jsonify({"ok": True, "empresa": _empresa_response.dump(empresa)}), 201
