"""Application factory de Flask."""

import logging

from flask import Flask, jsonify

from app.config import Config
from app.extensions import cors, limiter


def create_app(config_class: type = Config) -> Flask:
    """Crea y configura la instancia de Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Logging ──────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.DEBUG if app.config["FLASK_ENV"] == "development" else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── Extensiones ──────────────────────────────────────────────────────
    cors.init_app(app, origins=app.config["ALLOWED_ORIGINS"])
    limiter.init_app(app)

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.routes.contact import contact_bp  # noqa: E402
    app.register_blueprint(contact_bp)

    # ── Error handlers ───────────────────────────────────────────────────
    @app.errorhandler(429)
    def ratelimit_handler(_e):
        return jsonify({"ok": False, "errors": ["Demasiadas solicitudes. Inténtalo más tarde."]}), 429

    @app.errorhandler(500)
    def internal_error(_e):
        return jsonify({"ok": False, "errors": ["Error interno del servidor."]}), 500

    return app
