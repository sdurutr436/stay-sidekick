"""Blueprint de la ruta de contacto / solicitud de herramienta."""

import logging

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.services.contact import process_contact_form

logger = logging.getLogger(__name__)

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/api/contact", methods=["POST"])
@limiter.limit(lambda: __import__("flask").current_app.config["RATE_LIMIT_CONTACT"])
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

    # TODO: Aquí se conectará con el servicio de persistencia / email
    logger.info("Datos de contacto listos para procesar: %s", clean_data)

    return jsonify({"ok": True, "message": "Formulario recibido correctamente."}), 200
