"""Blueprint del formulario de contacto general (/empresa/contacto)."""

import logging

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.security.csrf import csrf_protect
from app.contact.service import process_contacto

logger = logging.getLogger(__name__)

contact_bp = Blueprint("contacto", __name__)


@contact_bp.route("/api/contacto", methods=["POST"])
@limiter.limit("10/hour")
@csrf_protect
def contacto():
    """Recibe y procesa el formulario de contacto general."""
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    clean_data, errors = process_contacto(json_data)

    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    return jsonify({"ok": True, "message": "Mensaje enviado correctamente."}), 200
