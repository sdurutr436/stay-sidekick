"""Tests de integración para el blueprint del formulario de contacto general."""

from unittest.mock import patch

import pytest
from flask import Flask


@pytest.fixture
def client():
    from app.extensions import limiter
    from app.contact.routes import contact_bp
    from app.solicitud.routes import solicitud_bp  # para /api/csrf-token

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["RATE_LIMIT_CONTACT"] = "100/hour"
    limiter.init_app(app)
    app.register_blueprint(contact_bp)
    app.register_blueprint(solicitud_bp)
    return app.test_client()


def _set_csrf(client) -> dict:
    resp = client.get("/api/csrf-token")
    token = resp.get_json()["csrf_token"]
    return {"X-CSRF-Token": token}


def test_contacto_sin_csrf_devuelve_403(client):
    resp = client.post("/api/contacto", json={"nombre": "Ana"})
    assert resp.status_code == 403


def test_contacto_sin_body_devuelve_400(client):
    headers = _set_csrf(client)
    resp = client.post("/api/contacto", headers=headers)
    assert resp.status_code == 400


def test_contacto_validacion_falla_devuelve_422(client):
    headers = _set_csrf(client)
    with patch(
        "app.contact.routes.process_contacto",
        return_value=({}, ["El campo mensaje es obligatorio."]),
    ):
        resp = client.post(
            "/api/contacto",
            headers=headers,
            json={"nombre": "Ana"},
        )
    assert resp.status_code == 422


def test_contacto_ok_devuelve_200(client):
    headers = _set_csrf(client)
    with patch(
        "app.contact.routes.process_contacto",
        return_value=({"nombre": "Ana"}, []),
    ):
        resp = client.post(
            "/api/contacto",
            headers=headers,
            json={"nombre": "Ana", "email": "a@x.com", "mensaje": "hola"},
        )
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
