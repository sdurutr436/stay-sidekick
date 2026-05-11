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
from app.extensions import cors, db, limiter, migrate


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
        from app import models  # noqa: F401  # pylint: disable=unused-import

    # ── Migraciones (Alembic vía Flask-Migrate) ───────────────────────────
    migrate.init_app(app, db)

    # ── Blueprints ───────────────────────────────────────────────────────
    from app.solicitud.routes import solicitud_bp                             # noqa: E402
    from app.auth.routes import auth_bp                                      # noqa: E402
    from app.empresas.routes import empresas_bp                              # noqa: E402
    from app.usuarios.routes import usuarios_bp                              # noqa: E402
    from app.h_maestro_apartamentos.routes import apartamentos_bp             # noqa: E402
    from app.h_sincronizador_contactos.routes import contactos_bp             # noqa: E402
    from app.h_notificaciones_tardias.routes import notificaciones_bp         # noqa: E402
    from app.h_vault_comunicaciones.routes import h_vault_comunicaciones_bp   # noqa: E402
    from app.perfil.routes import perfil_bp                                  # noqa: E402
    from app.h_mapa_de_calor.routes import heatmap_bp                        # noqa: E402
    from app.contact.routes import contact_bp                                # noqa: E402
    from app.docs.routes import docs_bp                                      # noqa: E402
    app.register_blueprint(solicitud_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(apartamentos_bp)
    app.register_blueprint(contactos_bp)
    app.register_blueprint(notificaciones_bp)
    app.register_blueprint(h_vault_comunicaciones_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(heatmap_bp)
    app.register_blueprint(contact_bp)

    # ── Healthcheck (Railway) ────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # ── Error handlers ───────────────────────────────────────────────────
    @app.errorhandler(429)
    def ratelimit_handler(_e):
        return jsonify({"ok": False, "errors": ["Demasiadas solicitudes. Inténtalo más tarde."]}), 429

    @app.errorhandler(500)
    def internal_error(_e):
        return jsonify({"ok": False, "errors": ["Error interno del servidor."]}), 500

    return app
