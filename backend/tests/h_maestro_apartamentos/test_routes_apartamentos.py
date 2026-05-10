"""Tests de integración para el blueprint de apartamentos."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-apartamentos"


def _token(empresa_id: str = "emp-1", rol: str = "admin") -> str:
    payload = {
        "sub": "admin@test.com",
        "user_id": "user-1",
        "empresa_id": empresa_id,
        "rol": rol,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.h_maestro_apartamentos.routes import apartamentos_bp
    from app.extensions import limiter

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(apartamentos_bp)
    return app.test_client()


def _auth():
    return {"Authorization": f"Bearer {_token()}"}


_APT_DICT = {"id": "apt-1", "nombre": "Apt 101", "ciudad": "Madrid", "id_pms": None, "id_externo": None,
             "direccion": None, "pms_origen": None, "activo": True}


# ── GET /api/apartamentos ──────────────────────────────────────────────────


def test_list_apartamentos_sin_token_devuelve_401(client):
    resp = client.get("/api/apartamentos")
    assert resp.status_code == 401


def test_list_apartamentos_devuelve_200(client):
    with patch("app.h_maestro_apartamentos.routes.service.list_apartamentos", return_value=[_APT_DICT]):
        resp = client.get("/api/apartamentos", headers=_auth())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert len(data["apartamentos"]) == 1


# ── POST /api/apartamentos ─────────────────────────────────────────────────


def test_crear_apartamento_sin_body_devuelve_400(client):
    resp = client.post("/api/apartamentos", headers=_auth(), content_type="application/json")
    assert resp.status_code == 400


def test_crear_apartamento_exitoso_devuelve_201(client):
    with patch("app.h_maestro_apartamentos.routes.service.create_apartamento", return_value=(_APT_DICT, [])):
        resp = client.post("/api/apartamentos", headers=_auth(), json={"nombre": "Apt 101"})
    assert resp.status_code == 201
    assert resp.get_json()["ok"] is True


def test_crear_apartamento_error_devuelve_422(client):
    with patch("app.h_maestro_apartamentos.routes.service.create_apartamento", return_value=(None, ["Nombre obligatorio."])):
        resp = client.post("/api/apartamentos", headers=_auth(), json={"nombre": ""})
    assert resp.status_code == 422


# ── GET /api/apartamentos/<id> ─────────────────────────────────────────────


def test_get_apartamento_no_encontrado_devuelve_404(client):
    with patch("app.h_maestro_apartamentos.routes.service.get_apartamento", return_value=(None, "Apartamento no encontrado.")):
        resp = client.get("/api/apartamentos/apt-x", headers=_auth())
    assert resp.status_code == 404


def test_get_apartamento_encontrado_devuelve_200(client):
    with patch("app.h_maestro_apartamentos.routes.service.get_apartamento", return_value=(_APT_DICT, None)):
        resp = client.get("/api/apartamentos/apt-1", headers=_auth())
    assert resp.status_code == 200


# ── POST /api/apartamentos/sincronizacion/smoobu ─────────────────────────


def test_sync_smoobu_error_devuelve_400(client):
    with patch("app.h_maestro_apartamentos.routes.service.sync_from_smoobu", return_value=(None, "PMS no configurado.")):
        resp = client.post("/api/apartamentos/sincronizacion/smoobu", headers=_auth())
    assert resp.status_code == 400


def test_sync_smoobu_exitoso_devuelve_200(client):
    resultado = {"total": 5, "nuevos": 2, "actualizados": 3}
    with patch("app.h_maestro_apartamentos.routes.service.sync_from_smoobu", return_value=(resultado, None)):
        resp = client.post("/api/apartamentos/sincronizacion/smoobu", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["resultado"]["nuevos"] == 2
