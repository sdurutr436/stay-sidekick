"""Tests de integración para el blueprint público de solicitud de acceso."""

from unittest.mock import patch

import pytest
from flask import Flask


@pytest.fixture
def client():
    from app.extensions import limiter
    from app.solicitud.routes import solicitud_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["RATE_LIMIT_CONTACT"] = "100/hour"
    limiter.init_app(app)
    app.register_blueprint(solicitud_bp)
    return app.test_client()


def _set_csrf(client) -> dict:
    """Pide token CSRF y devuelve cabeceras válidas para enviar."""
    resp = client.get("/api/csrf-token")
    token = resp.get_json()["csrf_token"]
    return {"X-CSRF-Token": token}


# ── GET /api/csrf-token ────────────────────────────────────────────────────


def test_csrf_token_devuelve_200_con_cookie_y_token(client):
    resp = client.get("/api/csrf-token")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["csrf_token"]
    # La cookie csrf_token debe haberse establecido
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "csrf_token=" in set_cookie


# ── POST /api/contact ──────────────────────────────────────────────────────


def test_solicitud_sin_csrf_devuelve_403(client):
    resp = client.post("/api/contact", json={"nombre": "Ana"})
    assert resp.status_code == 403


def test_solicitud_sin_body_devuelve_400(client):
    headers = _set_csrf(client)
    resp = client.post("/api/contact", headers=headers)
    assert resp.status_code == 400


def test_solicitud_validacion_falla_devuelve_422(client):
    headers = _set_csrf(client)
    with patch(
        "app.solicitud.routes.process_solicitud",
        return_value=({}, ["El campo email es obligatorio."]),
    ):
        resp = client.post(
            "/api/contact",
            headers=headers,
            json={"nombre": "Ana"},
        )
    assert resp.status_code == 422
    assert "obligatorio" in resp.get_json()["errors"][0]


def test_solicitud_captcha_falla_devuelve_403(client):
    headers = _set_csrf(client)
    with patch(
        "app.solicitud.routes.process_solicitud",
        return_value=({}, ["Verificación captcha fallida."]),
    ):
        resp = client.post(
            "/api/contact",
            headers=headers,
            json={"nombre": "Ana"},
        )
    assert resp.status_code == 403


def test_solicitud_ok_devuelve_200(client):
    headers = _set_csrf(client)
    with patch(
        "app.solicitud.routes.process_solicitud",
        return_value=({"nombre": "Ana"}, []),
    ):
        resp = client.post(
            "/api/contact",
            headers=headers,
            json={"nombre": "Ana", "email": "a@x.com", "mensaje": "hola"},
        )
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
