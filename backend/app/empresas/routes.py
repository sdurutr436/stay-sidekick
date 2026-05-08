"""Blueprint del módulo de empresas.

Rutas:
- GET /api/empresas → lista todas las empresas (solo superadmin)
"""

from flask import Blueprint, g, jsonify

from app.empresas.model import Empresa
from app.extensions import db
from app.security.jwt import jwt_required

empresas_bp = Blueprint("empresas", __name__)


@empresas_bp.route("/api/empresas", methods=["GET"])
@jwt_required
def list_empresas():
    if not g.jwt_claims.get("es_superadmin"):
        return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
    empresas = db.session.query(Empresa).filter_by(activa=True).order_by(Empresa.nombre).all()
    return jsonify({
        "ok": True,
        "empresas": [
            {"id": str(e.id), "nombre": e.nombre, "email": e.email}
            for e in empresas
        ],
    }), 200
