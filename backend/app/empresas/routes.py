"""Blueprint del módulo de empresas.

Rutas:
- GET    /api/empresas        → lista todas las empresas (solo superadmin)
- POST   /api/empresas        → crea empresa y envía correo de bienvenida
- DELETE /api/empresas/<id>   → borra una empresa y sus datos en cascada
"""

import logging

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.common.notifications.mail_service import send_welcome_company
from app.empresas.model import Empresa
from app.empresas.repository import crear_empresa
from app.empresas.schemas import CrearEmpresaSchema, EmpresaResponseSchema
from app.empresas.service import borrar_empresa_completa
from app.security.require_rol import require_rol

logger = logging.getLogger(__name__)

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

    try:
        created_at = getattr(empresa, "created_at", None)
        summary = [
            ("Nombre", empresa.nombre),
            ("Email registrado", empresa.email),
            (
                "Fecha de creación",
                created_at.strftime("%d/%m/%Y %H:%M UTC") if created_at else "",
            ),
        ]
        if not send_welcome_company(empresa.email, empresa.nombre, summary=summary):
            logger.warning("No se pudo enviar el correo de bienvenida a %s", empresa.email)
    except Exception:
        logger.exception("Excepción inesperada al enviar bienvenida a %s", empresa.email)

    return jsonify({"ok": True, "empresa": _empresa_response.dump(empresa)}), 201


@empresas_bp.route("/api/empresas/<uuid:empresa_id>", methods=["DELETE"])
@require_rol("superadmin")
def eliminar_empresa_route(empresa_id):
    eliminada = borrar_empresa_completa(str(empresa_id))
    if not eliminada:
        return jsonify({"ok": False, "errors": ["Empresa no encontrada."]}), 404
    return jsonify({"ok": True, "mensaje": "Empresa eliminada correctamente."}), 200
