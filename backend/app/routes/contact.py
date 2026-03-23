"""DEPRECATED: usa app.contact.routes en su lugar."""
from app.contact.routes import contact_bp  # noqa: F401

__all__ = ["contact_bp"]

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

    return jsonify({"ok": True, "message": "Formulario recibido correctamente."}), 200
