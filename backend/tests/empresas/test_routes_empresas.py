"""Tests de integración para el blueprint de empresas."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-empresas"


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


# ── GET /api/empresas ──────────────────────────────────────────────────────


def test_list_empresas_sin_token_devuelve_401(client):
    resp = client.get("/api/empresas")
    assert resp.status_code == 401


def test_list_empresas_no_superadmin_devuelve_403(client):
    resp = client.get("/api/empresas", headers=_auth(superadmin=False))
    assert resp.status_code == 403


def test_list_empresas_superadmin_devuelve_200(client):
    with patch("app.empresas.routes.Empresa") as MockEmpresa:
        fila = MagicMock()
        fila.id = "emp-id-1"
        fila.nombre = "Empresa Test"
        fila.email = "empresa@test.com"
        (
            MockEmpresa.query
            .with_entities.return_value
            .filter_by.return_value
            .order_by.return_value
            .all.return_value
        ) = [fila]
        resp = client.get("/api/empresas", headers=_auth(superadmin=True))
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert isinstance(data["empresas"], list)


# ── POST /api/empresas ─────────────────────────────────────────────────────


def test_crear_empresa_no_superadmin_devuelve_403(client):
    resp = client.post("/api/empresas", headers=_auth(superadmin=False), json={"nombre": "X", "email": "x@x.com"})
    assert resp.status_code == 403


def test_crear_empresa_sin_email_devuelve_422(client):
    resp = client.post("/api/empresas", headers=_auth(superadmin=True), json={"nombre": "Sin email"})
    assert resp.status_code == 422


def test_crear_empresa_exitosa_devuelve_201(client):
    # SimpleNamespace evita que Marshmallow trate el objeto como Mapping (dict)
    from types import SimpleNamespace
    empresa_mock = SimpleNamespace(id="emp-new", nombre="Nueva Empresa", email="nueva@test.com")
    with patch("app.empresas.routes.crear_empresa", return_value=empresa_mock):
        resp = client.post(
            "/api/empresas",
            headers=_auth(superadmin=True),
            json={"nombre": "Nueva Empresa", "email": "nueva@test.com"},
        )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["ok"] is True
    assert data["empresa"]["email"] == "nueva@test.com"
