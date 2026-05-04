"""Decorador de restricción de acceso por IP para endpoints de administración."""

from functools import wraps

from flask import current_app, jsonify, request


def require_admin_ip(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        allowed = current_app.config.get("AI_PROMPT_ADMIN_IPS", [])
        if request.remote_addr not in allowed:
            return jsonify({"ok": False, "errors": ["Acceso denegado."]}), 403
        return f(*args, **kwargs)
    return decorated
