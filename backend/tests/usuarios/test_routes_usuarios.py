"""Tests de integración para el blueprint de usuarios."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-usuarios"


def _token(rol: str = "admin", empresa_id: str = "emp-1", es_superadmin: bool = False) -> str:
    payload = {
        "sub": "admin@test.com",
        "user_id": "user-admin",
        "empresa_id": empresa_id,
        "rol": rol,
        "es_superadmin": es_superadmin,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.usuarios.routes import usuarios_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.register_blueprint(usuarios_bp)
    return app.test_client()


def _auth(rol="admin"):
    return {"Authorization": f"Bearer {_token(rol=rol)}"}


# ── GET /api/usuarios ──────────────────────────────────────────────────────


def test_list_usuarios_sin_token_devuelve_401(client):
    resp = client.get("/api/usuarios")
    assert resp.status_code == 401


def test_list_usuarios_operativo_devuelve_403(client):
    resp = client.get("/api/usuarios", headers=_auth("operativo"))
    assert resp.status_code == 403


def test_list_usuarios_admin_devuelve_200(client):
    with patch("app.usuarios.routes.service.listar_usuarios", return_value={"usuarios": [], "max_usuarios": 4}):
        resp = client.get("/api/usuarios", headers=_auth("admin"))
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


# ── POST /api/usuarios ─────────────────────────────────────────────────────


def test_crear_usuario_sin_body_devuelve_400(client):
    resp = client.post("/api/usuarios", headers=_auth("admin"), content_type="application/json")
    assert resp.status_code == 400


def test_crear_usuario_exitoso_devuelve_201(client):
    usuario = {"id": "u1", "email": "nuevo@test.com", "rol": "operativo", "activo": True, "created_at": None}
    with patch("app.usuarios.routes.service.crear_usuario", return_value=({"usuario": usuario, "password_temporal": "TEMP123"}, [])):
        resp = client.post("/api/usuarios", headers=_auth("admin"), json={"email": "nuevo@test.com", "rol": "operativo"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["ok"] is True
    assert "password_temporal" in data


def test_crear_usuario_error_validacion_devuelve_422(client):
    with patch("app.usuarios.routes.service.crear_usuario", return_value=(None, ["El correo ya está en uso."])):
        resp = client.post("/api/usuarios", headers=_auth("admin"), json={"email": "dup@test.com", "rol": "operativo"})
    assert resp.status_code == 422


# ── DELETE /api/usuarios/<id> ──────────────────────────────────────────────


def test_eliminar_usuario_no_encontrado_devuelve_404(client):
    with patch("app.usuarios.routes.service.eliminar_usuario", return_value=["Usuario no encontrado."]):
        resp = client.delete("/api/usuarios/u-x", headers=_auth("admin"))
    assert resp.status_code == 404


def test_eliminar_usuario_exitoso_devuelve_200(client):
    with patch("app.usuarios.routes.service.eliminar_usuario", return_value=[]):
        resp = client.delete("/api/usuarios/u-1", headers=_auth("admin"))
    assert resp.status_code == 200


# ── PATCH /api/usuarios/<id>/contrasena ───────────────────────────────────


def test_resetear_contrasena_exitoso_devuelve_200(client):
    with patch("app.usuarios.routes.service.resetear_password", return_value=({"password_temporal": "NUEVA123"}, [])):
        resp = client.patch("/api/usuarios/u-1/contrasena", headers=_auth("admin"))
    assert resp.status_code == 200
    assert "password_temporal" in resp.get_json()


def test_resetear_contrasena_no_encontrado_devuelve_404(client):
    with patch("app.usuarios.routes.service.resetear_password", return_value=(None, ["Usuario no encontrado."])):
        resp = client.patch("/api/usuarios/u-x/contrasena", headers=_auth("admin"))
    assert resp.status_code == 404
