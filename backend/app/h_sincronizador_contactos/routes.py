"""Blueprint de sincronización con Google Contacts.

Rutas (todas requieren JWT excepto el callback OAuth):
- GET    /api/contactos/google/auth               → genera URL de autorización OAuth
- GET    /api/contactos/google/callback            → intercambia código OAuth por tokens y redirige al frontend
- GET    /api/contactos/google/status              → estado de la conexión Google de la empresa
- DELETE /api/contactos/google/conexion            → revoca y elimina tokens OAuth (desconectar cuenta Google)
- GET    /api/contactos/preferencias               → obtiene preferencias de sincronización
- PUT    /api/contactos/preferencias               → guarda preferencias de sincronización
- POST   /api/contactos/sincronizacion             → [acción] PMS API + Google conectado: sincroniza reservas del PMS → Google Contacts (fechas en body)
- POST   /api/contactos/exportacion/csv            → [acción] PMS API + Google desconectado: genera CSV para importación manual (fechas en body)
- POST   /api/contactos/xlsx/sincronizacion        → [acción] XLSX + Google conectado: sincroniza desde XLSX subido → Google Contacts (file en multipart)
- POST   /api/contactos/xlsx/exportacion/csv       → [acción] XLSX + Google desconectado: genera CSV desde XLSX subido (file en multipart)
"""

import logging

from flask import Blueprint, g, jsonify, redirect, request

from app.extensions import limiter
from app.security.jwt import jwt_required
from app.h_sincronizador_contactos import service

logger = logging.getLogger(__name__)

contactos_bp = Blueprint("contactos", __name__)

_FRONTEND_BASE = "http://localhost:4200"


def _empresa_id() -> str:
    return g.jwt_claims["empresa_id"]


def _is_admin() -> bool:
    return g.jwt_claims.get("rol") == "admin"


def _frontend_url(path: str) -> str:
    from flask import current_app
    base = current_app.config.get("FRONTEND_BASE_URL", _FRONTEND_BASE)
    return f"{base.rstrip('/')}{path}"


# ── OAuth 2.0 ────────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/google/auth", methods=["GET"])
@jwt_required
def google_auth():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede conectar Google."]}), 403

    url = service.build_oauth_url(_empresa_id())
    return jsonify({"ok": True, "url": url}), 200


@contactos_bp.route("/api/contactos/google/callback", methods=["GET"])
def google_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")

    if error:
        logger.warning("OAuth Google denegado por el usuario: %s", error)
        return redirect(_frontend_url("/menu/perfil?google_error=acceso_denegado"))

    empresa_id = service.verify_oauth_state(state) if state else None

    if not empresa_id:
        logger.warning("OAuth Google: state inválido (posible CSRF)")
        return redirect(_frontend_url("/menu/perfil?google_error=estado_invalido"))

    if not code:
        return redirect(_frontend_url("/menu/perfil?google_error=codigo_invalido"))

    exito, error_msg = service.exchange_code_for_tokens(code, empresa_id)
    if not exito:
        logger.error("Error intercambiando tokens OAuth: %s", error_msg)
        return redirect(_frontend_url("/menu/perfil?google_error=token_fallido"))

    return redirect(_frontend_url("/menu/perfil?google_conectado=true"))


@contactos_bp.route("/api/contactos/google/status", methods=["GET"])
@jwt_required
def google_status():
    data = service.get_google_status(_empresa_id())
    return jsonify({"ok": True, "google": data}), 200


@contactos_bp.route("/api/contactos/google/conexion", methods=["DELETE"])
@jwt_required
def google_disconnect():
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede desconectar Google."]}), 403

    error = service.disconnect_google(_empresa_id())
    if error:
        return jsonify({"ok": False, "errors": [error]}), 404
    return jsonify({"ok": True}), 200


# ── Preferencias ─────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/preferencias", methods=["GET"])
@jwt_required
def get_preferencias():
    data = service.get_preferencias(_empresa_id())
    return jsonify({"ok": True, "preferencias": data}), 200


@contactos_bp.route("/api/contactos/preferencias", methods=["PUT"])
@jwt_required
def save_preferencias():
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_preferencias(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "preferencias": data}), 200


# ── Sincronización ────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/sincronizacion", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def sync_contacts():
    json_data = request.get_json(silent=True) or {}
    data, error = service.sync_contacts(_empresa_id(), json_data)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "resultado": data}), 200


# ── Export CSV ────────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/exportacion/csv", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def export_csv():
    json_data = request.get_json(silent=True) or {}
    csv_bytes, error = service.export_csv(_empresa_id(), json_data)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400

    from flask import Response
    return Response(
        csv_bytes,
        status=200,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=contactos_google.csv"},
    )


# ── XLSX upload ───────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/xlsx/sincronizacion", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def xlsx_sync():
    if "file" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba un campo 'file' con el archivo."]}), 400

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo debe tener extensión .xlsx."]}), 400

    file_bytes = f.read()
    data, error = service.sync_from_xlsx(_empresa_id(), file_bytes)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "resultado": data}), 200


@contactos_bp.route("/api/contactos/xlsx/exportacion/csv", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def xlsx_export_csv():
    if "file" not in request.files:
        return jsonify({"ok": False, "errors": ["Se esperaba un campo 'file' con el archivo."]}), 400

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".xlsx"):
        return jsonify({"ok": False, "errors": ["El archivo debe tener extensión .xlsx."]}), 400

    file_bytes = f.read()
    csv_bytes, error = service.export_csv_from_xlsx(_empresa_id(), file_bytes)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400

    from flask import Response
    return Response(
        csv_bytes,
        status=200,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=contactos_google.csv"},
    )
