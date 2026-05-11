"""Blueprint del Vault de comunicaciones.

Rutas (todas requieren JWT salvo los endpoints de admin por IP):
- GET    /api/vault/plantillas                          → listar plantillas
- POST   /api/vault/plantillas                          → crear plantilla
- PUT    /api/vault/plantillas/<id>                     → actualizar plantilla
- DELETE /api/vault/plantillas/<id>                     → soft-delete
- POST   /api/vault/plantillas/<id>/mejoras             → mejorar con IA
- POST   /api/vault/plantillas/<id>/traducciones        → traducir con IA
- GET    /api/ai/uso                                    → contadores de uso IA
- GET    /api/ai/config                                 → config IA enmascarada (solo admin)
- GET    /api/admin/system-prompts/<nombre>             → leer system prompt (solo IP whitelist)
- PUT    /api/admin/system-prompts/<nombre>             → actualizar system prompt (solo IP whitelist)
"""

import logging

from flask import Blueprint, g, jsonify, request

from app.common import ai_service
from app.common.crypto import decrypt
from app.extensions import db
from app.h_vault_comunicaciones import service
from app.h_vault_comunicaciones.model import SystemPrompt
from app.h_vault_comunicaciones.schemas import (
    ActualizarPlantillaSchema,
    CrearPlantillaSchema,
    MejorarSchema,
    PlantillaResponseSchema,
    TraducirSchema,
)
from app.perfil.model import ConfiguracionIA
from app.security.ip_whitelist import require_admin_ip
from app.security.jwt import jwt_required
from app.security.require_rol import require_rol

logger = logging.getLogger(__name__)

h_vault_comunicaciones_bp = Blueprint("h_vault_comunicaciones", __name__)

_crear_schema = CrearPlantillaSchema()
_actualizar_schema = ActualizarPlantillaSchema()
_mejorar_schema = MejorarSchema()
_traducir_schema = TraducirSchema()
_plantilla_response = PlantillaResponseSchema()
_plantillas_response = PlantillaResponseSchema(many=True)


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


def _flatten(messages: dict) -> list[str]:
    result = []
    for msgs in messages.values():
        result.extend(msgs)
    return result


def _handle_ia_error(exc: Exception):
    if isinstance(exc, ValueError):
        msg = str(exc)
        if msg == "LIMIT_DAILY":
            return jsonify({
                "ok": False,
                "errors": ["Has alcanzado el límite diario de IA. Configura tu API key en Perfil > IA."],
            }), 429
        if msg == "LIMIT_WEEKLY":
            return jsonify({
                "ok": False,
                "errors": ["Has alcanzado el límite semanal de IA. Configura tu API key en Perfil > IA."],
            }), 429
        if msg == "RATE_LIMIT_SYSTEM":
            return jsonify({
                "ok": False,
                "errors": ["El proveedor de IA del sistema ha alcanzado su límite de tráfico. Inténtalo en unos minutos o configura tu propia API key en Perfil > IA."],
            }), 429
        if msg == "RATE_LIMIT_BYOK":
            return jsonify({
                "ok": False,
                "errors": ["Tu proveedor de IA ha rechazado la petición por exceso de tráfico. Inténtalo en unos minutos."],
            }), 429
    if isinstance(exc, TimeoutError):
        return jsonify({"ok": False, "errors": ["El servicio de IA tardó demasiado. Inténtalo de nuevo."]}), 504
    logger.exception("Error inesperado conectando con el servicio de IA")
    return jsonify({"ok": False, "errors": ["Error al conectar con el servicio de IA."]}), 502


# ── Plantillas ────────────────────────────────────────────────────────────────


@h_vault_comunicaciones_bp.route("/api/vault/plantillas", methods=["GET"])
@jwt_required
def list_plantillas():
    categoria = request.args.get("categoria") or None
    idioma = request.args.get("idioma") or None
    plantillas = service.list_plantillas(_empresa_id(), categoria, idioma)
    return jsonify({"ok": True, "plantillas": _plantillas_response.dump(plantillas)}), 200


@h_vault_comunicaciones_bp.route("/api/vault/plantillas", methods=["POST"])
@jwt_required
def crear_plantilla():
    body = request.get_json(silent=True) or {}
    errors = _crear_schema.validate(body)
    if errors:
        return jsonify({"ok": False, "errors": _flatten(errors)}), 422
    data = _crear_schema.load(body)
    plantilla = service.crear_plantilla(_empresa_id(), data)
    return jsonify({"ok": True, "plantilla": _plantilla_response.dump(plantilla)}), 201


@h_vault_comunicaciones_bp.route("/api/vault/plantillas/<uuid:plantilla_id>", methods=["PUT"])
@jwt_required
def actualizar_plantilla(plantilla_id):
    body = request.get_json(silent=True) or {}
    errors = _actualizar_schema.validate(body)
    if errors:
        return jsonify({"ok": False, "errors": _flatten(errors)}), 422
    data = _actualizar_schema.load(body)
    plantilla, error = service.actualizar_plantilla(str(plantilla_id), _empresa_id(), data)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True, "plantilla": _plantilla_response.dump(plantilla)}), 200


@h_vault_comunicaciones_bp.route("/api/vault/plantillas/<uuid:plantilla_id>", methods=["DELETE"])
@jwt_required
def eliminar_plantilla(plantilla_id):
    error = service.eliminar_plantilla(str(plantilla_id), _empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200


# ── IA — mejorar / traducir ───────────────────────────────────────────────────


@h_vault_comunicaciones_bp.route("/api/vault/plantillas/<uuid:plantilla_id>/mejoras", methods=["POST"])
@jwt_required
def mejorar_plantilla(plantilla_id):
    if not service.get_plantilla(str(plantilla_id), _empresa_id()):
        return jsonify({"ok": False, "errors": ["Plantilla no encontrada."]}), 404

    body = request.get_json(silent=True) or {}
    errors = _mejorar_schema.validate(body)
    if errors:
        return jsonify({"ok": False, "errors": _flatten(errors)}), 422
    data = _mejorar_schema.load(body)

    try:
        contenido = ai_service.mejorar(data["contenido"], data["idioma"], _empresa_id())
    except Exception as exc:
        return _handle_ia_error(exc)

    return jsonify({"ok": True, "contenido": contenido}), 200


@h_vault_comunicaciones_bp.route("/api/vault/plantillas/<uuid:plantilla_id>/traducciones", methods=["POST"])
@jwt_required
def traducir_plantilla(plantilla_id):
    if not service.get_plantilla(str(plantilla_id), _empresa_id()):
        return jsonify({"ok": False, "errors": ["Plantilla no encontrada."]}), 404

    body = request.get_json(silent=True) or {}
    errors = _traducir_schema.validate(body)
    if errors:
        return jsonify({"ok": False, "errors": _flatten(errors)}), 422
    data = _traducir_schema.load(body)

    try:
        contenido = ai_service.traducir(data["contenido"], data["idioma_destino"], _empresa_id())
    except Exception as exc:
        return _handle_ia_error(exc)

    return jsonify({"ok": True, "contenido": contenido}), 200


# ── IA — uso y config ─────────────────────────────────────────────────────────


@h_vault_comunicaciones_bp.route("/api/ai/uso", methods=["GET"])
@jwt_required
def get_uso():
    uso = ai_service.get_uso(_empresa_id())
    return jsonify({"ok": True, **uso}), 200


@h_vault_comunicaciones_bp.route("/api/ai/config", methods=["GET"])
@require_rol("admin")
def get_ai_config():
    config_ia = db.session.query(ConfiguracionIA).filter_by(empresa_id=_empresa_id()).first()
    if not config_ia:
        return jsonify({"ok": True, "data": {"configurado": False, "proveedor": None, "modelo": None, "api_key_masked": None}}), 200

    api_key_masked = None
    if config_ia.api_key_cifrada:
        key = decrypt(config_ia.api_key_cifrada) or ""
        if len(key) > 8:
            api_key_masked = key[:4] + "*" * max(0, len(key) - 8) + key[-4:]
        else:
            api_key_masked = "****"

    return jsonify({
        "ok": True,
        "data": {
            "configurado": True,
            "proveedor": config_ia.proveedor,
            "modelo": config_ia.modelo,
            "api_key_masked": api_key_masked,
        },
    }), 200


# ── Admin — system prompts (solo IP whitelist, sin JWT) ───────────────────────


@h_vault_comunicaciones_bp.route("/api/admin/system-prompts/<string:nombre>", methods=["GET"])
@require_admin_ip
def get_system_prompt(nombre):
    row = db.session.get(SystemPrompt, nombre)
    if not row:
        return jsonify({"ok": False, "errors": ["System prompt no encontrado."]}), 404
    return jsonify({"ok": True, "nombre": row.nombre, "contenido": row.contenido}), 200


@h_vault_comunicaciones_bp.route("/api/admin/system-prompts/<string:nombre>", methods=["PUT"])
@require_admin_ip
def upsert_system_prompt(nombre):
    body = request.get_json(silent=True) or {}
    contenido = body.get("contenido", "")
    if not contenido:
        return jsonify({"ok": False, "errors": ["El campo contenido es obligatorio."]}), 422

    from datetime import datetime, timezone
    row = db.session.get(SystemPrompt, nombre)
    if row:
        row.contenido = contenido
        row.updated_at = datetime.now(timezone.utc)
    else:
        db.session.add(SystemPrompt(nombre=nombre, contenido=contenido))
    db.session.commit()

    ai_service.invalidar_cache(nombre)
    return jsonify({"ok": True}), 200
