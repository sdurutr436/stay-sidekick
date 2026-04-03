"""Blueprint de autenticación.

Rutas:
- POST /api/auth/login  → sanitiza, verifica credenciales y emite JWT

Seguridad aplicada:
- CORS (a nivel de app)
- Rate limiting estricto (10/hour por IP)
- CSRF stateless (Double-Submit Cookie)
- Sanitización + validación Marshmallow (LoginSchema)
- bcrypt para verificación de contraseña
- Mensaje de error genérico (no revela si el email existe)
"""

import logging

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.security.csrf import csrf_protect
from app.auth.service import authenticate_user, sanitize_login_payload

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("10/hour")
@csrf_protect
def login():
    """Autentica al usuario y devuelve un JWT si las credenciales son válidas.

    Flujo:
    1. Parsear JSON del body.
    2. Sanitizar y validar con LoginSchema.
    3. Verificar credenciales contra la BD (user_repository).
    4. Emitir JWT firmado con HS256.

    Respuestas:
    - 200 { ok: true, token: "<jwt>" }
    - 400 body no es JSON válido
    - 401 credenciales incorrectas (mensaje genérico)
    - 422 errores de validación del payload
    - 403 CSRF inválido (gestionado por @csrf_protect)
    - 429 rate limit superado (gestionado por @limiter)
    """
    json_data = request.get_json(silent=True)
    if not json_data:
        return jsonify({"ok": False, "errors": ["Se esperaba un cuerpo JSON."]}), 400

    # Capa 1: sanitización y validación del payload
    clean_data, errors = sanitize_login_payload(json_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 422

    # Capa 2: verificación de credenciales y emisión de JWT
    token, errors = authenticate_user(clean_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 401

    return jsonify({"ok": True, "token": token}), 200
