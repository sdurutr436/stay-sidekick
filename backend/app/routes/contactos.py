"""Blueprint de sincronización con Google Contacts.

Rutas (todas requieren JWT excepto el callback OAuth):
- GET    /api/contactos/google/auth          → genera URL de autorización OAuth
- GET    /api/contactos/google/callback      → intercambia código por tokens (redirect)
- GET    /api/contactos/google/status        → estado de la conexión Google
- DELETE /api/contactos/google/disconnect    → desconecta la cuenta Google
- GET    /api/contactos/preferencias         → obtiene preferencias de sincronización
- PUT    /api/contactos/preferencias         → guarda preferencias de sincronización
- POST   /api/contactos/sync                 → lanza sincronización PMS API → Google Contacts
- POST   /api/contactos/export/csv           → exporta CSV fallback (fuente: PMS API)
- POST   /api/contactos/xlsx/sync            → sincroniza desde XLSX subido (multipart)
- POST   /api/contactos/xlsx/export/csv      → exporta CSV desde XLSX subido (multipart)
"""

import logging

from flask import Blueprint, g, jsonify, redirect, request, session

from app.extensions import limiter
from app.security.jwt import jwt_required
from app.services import google_contacts as service

logger = logging.getLogger(__name__)

contactos_bp = Blueprint("contactos", __name__)

_FRONTEND_BASE = "http://localhost:4200"       # sobreescrito por FRONTEND_BASE_URL en config


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
    """Genera la URL de autorización OAuth y la devuelve en JSON. Solo admin."""
    if not _is_admin():
        return jsonify({"ok": False, "errors": ["Solo el administrador puede conectar Google."]}), 403

    url, state = service.build_oauth_url(_empresa_id())
    session["google_oauth_state"] = state
    session["google_oauth_empresa_id"] = _empresa_id()
    return jsonify({"ok": True, "url": url}), 200


@contactos_bp.route("/api/contactos/google/callback", methods=["GET"])
def google_callback():
    """Recibe el código OAuth de Google, intercambia por tokens y redirige al frontend."""
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")

    if error:
        logger.warning("OAuth Google denegado por el usuario: %s", error)
        return redirect(_frontend_url("/menu/perfil?google_error=acceso_denegado"))

    # Verificar state anti-CSRF
    expected_state = session.pop("google_oauth_state", None)
    empresa_id = session.pop("google_oauth_empresa_id", None)

    if not state or state != expected_state:
        logger.warning("OAuth Google: state inválido (posible CSRF)")
        return redirect(_frontend_url("/menu/perfil?google_error=estado_invalido"))

    if not code or not empresa_id:
        return redirect(_frontend_url("/menu/perfil?google_error=codigo_invalido"))

    exito, error_msg = service.exchange_code_for_tokens(code, empresa_id)
    if not exito:
        logger.error("Error intercambiando tokens OAuth: %s", error_msg)
        return redirect(_frontend_url("/menu/perfil?google_error=token_fallido"))

    return redirect(_frontend_url("/menu/perfil?google_conectado=true"))


@contactos_bp.route("/api/contactos/google/status", methods=["GET"])
@jwt_required
def google_status():
    """Devuelve el estado de la integración Google de la empresa."""
    data = service.get_google_status(_empresa_id())
    return jsonify({"ok": True, "google": data}), 200


@contactos_bp.route("/api/contactos/google/disconnect", methods=["DELETE"])
@jwt_required
def google_disconnect():
    """Desconecta la cuenta Google (elimina los tokens almacenados). Solo admin."""
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
    """Devuelve las preferencias de sincronización de contactos."""
    data = service.get_preferencias(_empresa_id())
    return jsonify({"ok": True, "preferencias": data}), 200


@contactos_bp.route("/api/contactos/preferencias", methods=["PUT"])
@jwt_required
def save_preferencias():
    """Guarda las preferencias de sincronización de contactos."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    data, errors = service.save_preferencias(_empresa_id(), json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422
    return jsonify({"ok": True, "preferencias": data}), 200


# ── Sincronización ────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/sync", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def sync_contacts():
    """Lanza la sincronización de reservas del PMS hacia Google Contacts."""
    json_data = request.get_json(silent=True) or {}
    data, error = service.sync_contacts(_empresa_id(), json_data)
    if error:
        return jsonify({"ok": False, "errors": [error]}), 400
    return jsonify({"ok": True, "resultado": data}), 200


# ── Export CSV ────────────────────────────────────────────────────────────


@contactos_bp.route("/api/contactos/export/csv", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def export_csv():
    """Exporta contactos en formato CSV de Google para importación manual (fuente: PMS API)."""
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


@contactos_bp.route("/api/contactos/xlsx/sync", methods=["POST"])
@limiter.limit("10/hour")
@jwt_required
def xlsx_sync():
    """Sincroniza contactos a Google desde un XLSX subido (multipart/form-data).

    Espera el campo ``file`` con el archivo .xlsx. Los datos se procesan
    en memoria y no se persisten (cumplimiento RGPD).
    """
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


@contactos_bp.route("/api/contactos/xlsx/export/csv", methods=["POST"])
@limiter.limit("20/hour")
@jwt_required
def xlsx_export_csv():
    """Exporta CSV de Google Contacts desde un XLSX subido (multipart/form-data).

    Espera el campo ``file`` con el archivo .xlsx. No requiere cuenta Google
    conectada. Los datos se procesan en memoria y no se persisten (RGPD).
    """
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
