"""Blueprint del módulo de empresas.

Rutas:
- GET /api/empresas → lista todas las empresas (solo superadmin)
"""

from flask import Blueprint, g, jsonify

from app.empresas.model import Empresa
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
