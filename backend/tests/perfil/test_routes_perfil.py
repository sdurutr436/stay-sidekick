"""Tests de integración para el blueprint de perfil."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-perfil"


def _token(rol: str = "admin", user_id: str = "user-1", empresa_id: str = "emp-1") -> str:
    payload = {
        "sub": "admin@test.com",
        "user_id": user_id,
        "empresa_id": empresa_id,
        "rol": rol,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.perfil.routes import perfil_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.register_blueprint(perfil_bp)
    return app.test_client()


def _auth(rol="admin"):
    return {"Authorization": f"Bearer {_token(rol=rol)}"}


# ── GET /api/perfil ────────────────────────────────────────────────────────


def test_get_perfil_sin_token_devuelve_401(client):
    resp = client.get("/api/perfil")
    assert resp.status_code == 401


def test_get_perfil_no_encontrado_devuelve_404(client):
    with patch("app.perfil.routes.service.get_perfil", return_value=None):
        resp = client.get("/api/perfil", headers=_auth())
    assert resp.status_code == 404


def test_get_perfil_exitoso_devuelve_200(client):
    perfil = {"id": "user-1", "email": "admin@test.com", "rol": "admin"}
    with patch("app.perfil.routes.service.get_perfil", return_value=perfil):
        resp = client.get("/api/perfil", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


# ── PUT /api/perfil/password ───────────────────────────────────────────────


def test_cambiar_password_sin_body_devuelve_400(client):
    resp = client.put("/api/perfil/password", headers=_auth(), content_type="application/json")
    assert resp.status_code == 400


def test_cambiar_password_error_devuelve_422(client):
    with patch("app.perfil.routes.service.cambiar_password", return_value=["La contraseña actual es incorrecta."]):
        resp = client.put("/api/perfil/password", headers=_auth(), json={"password_actual": "X", "password_nuevo": "Y"})
    assert resp.status_code == 422


def test_cambiar_password_exitoso_devuelve_200(client):
    with patch("app.perfil.routes.service.cambiar_password", return_value=[]):
        resp = client.put("/api/perfil/password", headers=_auth(), json={"password_actual": "old", "password_nuevo": "new"})
    assert resp.status_code == 200


# ── PUT /api/perfil/integraciones/pms (solo admin) ────────────────────────


def test_actualizar_pms_operativo_devuelve_403(client):
    resp = client.put("/api/perfil/integraciones/pms", headers=_auth("operativo"), json={"proveedor": "smoobu", "api_key": "k"})
    assert resp.status_code == 403


def test_actualizar_pms_admin_sin_body_devuelve_400(client):
    resp = client.put("/api/perfil/integraciones/pms", headers=_auth("admin"), content_type="application/json")
    assert resp.status_code == 400


# ── GET /api/perfil/integraciones ─────────────────────────────────────────


def test_get_integraciones_devuelve_200(client):
    with patch("app.perfil.routes.service.get_integraciones", return_value={"pms": None, "ia": None}):
        resp = client.get("/api/perfil/integraciones", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
