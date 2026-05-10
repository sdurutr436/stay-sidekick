"""Tests de integración para el blueprint de autenticación."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-auth"
_CSRF_TOKEN = "test-csrf-token-fijo"


def _token() -> str:
    payload = {
        "sub": "admin@test.com",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture
def client():
    """Cliente de test con función de scope para cookie jar limpio en cada test."""
    from app.auth.routes import auth_bp
    from app.extensions import limiter

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(auth_bp)
    return app.test_client()


def _set_csrf(client):
    """Establece la cookie CSRF en el jar del cliente de test."""
    client.set_cookie("csrf_token", _CSRF_TOKEN)
    return {"X-CSRF-Token": _CSRF_TOKEN}


# ── POST /api/auth/login ───────────────────────────────────────────────────


def test_login_sin_csrf_devuelve_403(client):
    """Sin token CSRF la petición es rechazada antes de procesar el JSON."""
    resp = client.post("/api/auth/login", json={"email": "a@a.com", "password": "x"})
    assert resp.status_code == 403


def test_login_sin_json_devuelve_400(client):
    csrf_headers = _set_csrf(client)
    resp = client.post(
        "/api/auth/login",
        data="no-json",
        content_type="text/plain",
        headers=csrf_headers,
    )
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_login_credenciales_invalidas_devuelve_401(client):
    csrf_headers = _set_csrf(client)
    with patch("app.auth.routes.authenticate_user", return_value=(None, ["Credenciales incorrectas."], False)), \
         patch("app.auth.routes.sanitize_login_payload", return_value=({"email": "x@x.com", "password": "wrong"}, [])):
        resp = client.post(
            "/api/auth/login",
            json={"email": "x@x.com", "password": "wrong"},
            headers=csrf_headers,
        )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["ok"] is False
    assert "Credenciales incorrectas." in data["errors"]


def test_login_exitoso_devuelve_token(client):
    csrf_headers = _set_csrf(client)
    with patch("app.auth.routes.authenticate_user", return_value=("jwt-fake", [], False)), \
         patch("app.auth.routes.sanitize_login_payload", return_value=({"email": "a@a.com", "password": "ok"}, [])):
        resp = client.post(
            "/api/auth/login",
            json={"email": "a@a.com", "password": "ok"},
            headers=csrf_headers,
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert "token" in data


# ── GET /api/auth/validacion ───────────────────────────────────────────────


def test_validacion_sin_header_devuelve_401(client):
    resp = client.get("/api/auth/validacion")
    assert resp.status_code == 401


def test_validacion_token_invalido_devuelve_401(client):
    resp = client.get("/api/auth/validacion", headers={"Authorization": "Bearer token-invalido"})
    assert resp.status_code == 401


def test_validacion_token_valido_devuelve_200(client):
    resp = client.get("/api/auth/validacion", headers={"Authorization": f"Bearer {_token()}"})
    assert resp.status_code == 200
