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
import time

from flask import Blueprint, jsonify, request

from app.extensions import limiter
from app.security.csrf import csrf_protect
from app.auth.service import authenticate_user, sanitize_login_payload
from app.security.jwt import decode_token

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
    token, errors, debe_cambiar = authenticate_user(clean_data)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 401

    return jsonify({"ok": True, "token": token, "debe_cambiar_password": debe_cambiar}), 200


@auth_bp.route("/api/auth/verify", methods=["GET"])
def verify_token():
    """Endpoint interno para auth_request de Nginx. No invocar desde el cliente.

    Devuelve 200 si el JWT es válido, 401 en cualquier otro caso.
    No expone información sobre el motivo del rechazo.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return "", 401

    token = auth_header[7:]
    claims = decode_token(token)

    if claims is None:
        return "", 401

    # Validación explícita de iat: debe estar presente y no en el futuro
    # (tolerancia de 5s para desfase de reloj entre contenedores)
    iat = claims.get("iat")
    if iat is None or iat > time.time() + 5:
        return "", 401

    return "", 200
