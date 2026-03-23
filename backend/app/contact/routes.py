"""Blueprint de la ruta de contacto / solicitud de herramienta.

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
from app.contact.service import process_contact_form

logger = logging.getLogger(__name__)

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/api/csrf-token", methods=["GET"])
@limiter.limit("30/hour")
def get_csrf_token():
    """Emite un token CSRF como cookie + respuesta JSON.

    El frontend debe:
    1. Llamar a GET /api/csrf-token antes de enviar el formulario.
    2. Leer la cookie ``csrf_token``.
    3. Incluir el valor en la cabecera ``X-CSRF-Token`` del POST.
    """
    token = generate_csrf_token()
    response = jsonify({"ok": True, "csrf_token": token})
    set_csrf_cookie(response, token)
    return response


@contact_bp.route("/api/contact", methods=["POST"])
@limiter.limit(lambda: __import__("flask").current_app.config["RATE_LIMIT_CONTACT"])
@csrf_protect
def contact():
    """Recibe y procesa el formulario de contacto.

    Espera un JSON con los campos definidos en ``ContactFormSchema``.
    Devuelve 200 si todo es correcto, 422 si hay errores de validación,
    o 403 si el captcha falla.
    """
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    clean_data, errors = process_contact_form(json_data)

    if errors:
        status = 403 if "captcha" in " ".join(errors).lower() else 422
        return jsonify({"ok": False, "errors": errors}), status

    return jsonify({"ok": True, "message": "Formulario recibido correctamente."}), 200
