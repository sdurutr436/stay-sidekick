"""Blueprint del formulario público de solicitud de acceso a Stay Sidekick.

Seguridad aplicada (sin sesión):
- CORS (flask-cors, a nivel de app)
- Rate limiting (flask-limiter)
- CSRF stateless (Double-Submit Cookie)
- Honeypot (campo oculto en Marshmallow schema)
- Captcha Turnstile (verificación server-side)
- Sanitización de entrada (nh3 + validadores)
"""

import logging

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.security.csrf import csrf_protect, generate_csrf_token, set_csrf_cookie
from app.solicitud.service import process_solicitud

logger = logging.getLogger(__name__)

solicitud_bp = Blueprint("formulario_solicitud", __name__)


@solicitud_bp.route("/api/csrf-token", methods=["GET"])
@limiter.limit("30/hour")
def get_csrf_token():
    """Emite un token CSRF como cookie + respuesta JSON."""
    token = generate_csrf_token()
    response = jsonify({"ok": True, "csrf_token": token})
    set_csrf_cookie(response, token)
    return response


@solicitud_bp.route("/api/contact", methods=["POST"])
@limiter.limit(lambda: __import__("flask").current_app.config["RATE_LIMIT_CONTACT"])
@csrf_protect
def solicitud():
    """Recibe y procesa el formulario público de solicitud."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    clean_data, errors = process_solicitud(json_data)

    if errors:
        status = 403 if "captcha" in " ".join(errors).lower() else 422
        return jsonify({"ok": False, "errors": errors}), status

    return jsonify({"ok": True, "message": "Solicitud recibida correctamente."}), 200
