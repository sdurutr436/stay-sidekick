"""Application factory de Flask.

Estructura del proyecto:
    app/
    ├── common/         → Utilidades compartidas (sanitizers, notifications, parsers)
    ├── security/       → CSRF, honeypot, JWT
    ├── exceptions/     → Excepciones personalizadas
    ├── models/         → Modelos de datos
    ├── repositories/   → Repositorios de datos
    ├── routes/         → Blueprints: formulario_solicitud, contactos, apartamentos, auth
    ├── schemas/        → Schemas Marshmallow por feature
    └── services/       → Servicios por feature (formulario_solicitud, google_contacts, etc.)
"""

import logging

from flask import Flask, jsonify

from app.config import Config
from app.extensions import cors, db, limiter


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
    cors.init_app(
        app,
        origins=app.config["ALLOWED_ORIGINS"],
        supports_credentials=True,  # necesario para cookies CSRF
    )
    limiter.init_app(app)
    db.init_app(app)

    # ── Modelos (registro en metadata de SQLAlchemy) ──────────────────────
    with app.app_context():
        import app.models  # noqa: F401

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.routes.formulario_solicitud import formulario_solicitud_bp  # noqa: E402
    from app.auth.routes import auth_bp                                  # noqa: E402
    from app.apartamentos.routes import apartamentos_bp                  # noqa: E402
    from app.routes.contactos import contactos_bp                        # noqa: E402
    app.register_blueprint(formulario_solicitud_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(apartamentos_bp)
    app.register_blueprint(contactos_bp)

    # ── Error handlers ───────────────────────────────────────────────────
    @app.errorhandler(429)
    def ratelimit_handler(_e):
        return jsonify({"ok": False, "errors": ["Demasiadas solicitudes. Inténtalo más tarde."]}), 429

    @app.errorhandler(500)
    def internal_error(_e):
        return jsonify({"ok": False, "errors": ["Error interno del servidor."]}), 500

    return app
