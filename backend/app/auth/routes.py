"""Blueprint de autenticación.

Rutas:
- POST /api/auth/login   → valida y sanitiza credenciales (lógica real en siguiente commit)

Seguridad aplicada:
- CORS (a nivel de app)
- Rate limiting
- CSRF stateless (Double-Submit Cookie)
- Sanitización + validación Marshmallow (LoginSchema)
"""

import logging

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.security.csrf import csrf_protect, generate_csrf_token, set_csrf_cookie
from app.auth.service import sanitize_login_payload

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("10/hour")
@csrf_protect
def login():
    """Recibe las credenciales, las sanitiza y prepara la autenticación.

    Actualmente devuelve 501 tras la sanitización — la verificación real
    contra la base de datos se implementa en el siguiente commit.
    """
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    clean_data, errors = sanitize_login_payload(json_data)

    if errors:
        # 422 para errores de validación (no revelar si el email existe)
        return jsonify({"ok": False, "errors": errors}), 422

    # TODO: verificar credenciales contra BD y emitir JWT (siguiente commit)
    return jsonify({"ok": False, "errors": ["Login no implementado aún."]}), 501
