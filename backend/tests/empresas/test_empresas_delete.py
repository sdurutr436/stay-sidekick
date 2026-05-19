"""Tests del endpoint DELETE /api/empresas/<id> y el servicio asociado."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-empresas-delete"


def _token(es_superadmin: bool = True) -> str:
    payload = {
        "sub": "super@test.com",
        "user_id": "super-1",
        "empresa_id": "emp-1",
        "rol": "admin",
        "es_superadmin": es_superadmin,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.empresas.routes import empresas_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.register_blueprint(empresas_bp)
    return app.test_client()


def _auth(superadmin=True):
    return {"Authorization": f"Bearer {_token(es_superadmin=superadmin)}"}


def test_delete_empresa_happy_path_devuelve_200(client):
    empresa_id = uuid.uuid4()
    with patch("app.empresas.routes.borrar_empresa_completa", return_value=True) as borrar_mock:
        resp = client.delete(f"/api/empresas/{empresa_id}", headers=_auth(superadmin=True))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["mensaje"] == "Empresa eliminada correctamente."
    borrar_mock.assert_called_once_with(str(empresa_id))


def test_delete_empresa_inexistente_devuelve_404(client):
    empresa_id = uuid.uuid4()
    with patch("app.empresas.routes.borrar_empresa_completa", return_value=False):
        resp = client.delete(f"/api/empresas/{empresa_id}", headers=_auth(superadmin=True))
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["ok"] is False
    assert "Empresa no encontrada." in data["errors"]


def test_delete_empresa_sin_superadmin_devuelve_403(client):
    empresa_id = uuid.uuid4()
    with patch("app.empresas.routes.borrar_empresa_completa") as borrar_mock:
        resp = client.delete(f"/api/empresas/{empresa_id}", headers=_auth(superadmin=False))
    assert resp.status_code == 403
    borrar_mock.assert_not_called()


def test_delete_empresa_sin_token_devuelve_401(client):
    resp = client.delete(f"/api/empresas/{uuid.uuid4()}")
    assert resp.status_code == 401


def test_delete_empresa_uuid_invalido_devuelve_404(client):
    resp = client.delete("/api/empresas/no-es-uuid", headers=_auth(superadmin=True))
    assert resp.status_code == 404
