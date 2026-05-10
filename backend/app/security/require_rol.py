"""Decorador de autorización por rol para rutas Flask.

Uso:
    @bp.route("...")
    @require_rol("admin")            # solo admin
    @require_rol("admin", "superadmin")  # admin o superadmin
    def mi_vista(): ...

Incluye jwt_required implícitamente: no añadir @jwt_required por separado.
"""

from functools import wraps

from flask import g, jsonify

from app.security.jwt import jwt_required


def require_rol(*roles: str):
    """Decorador de autorización por rol. Incluye validación JWT.

    Roles válidos: 'admin', 'operativo', 'superadmin' (es_superadmin=True).
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            claims = g.jwt_claims
            if "superadmin" in roles and claims.get("es_superadmin"):
                return f(*args, **kwargs)
            if claims.get("rol") in roles:
                return f(*args, **kwargs)
            return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
        return jwt_required(wrapped)
    return decorator
