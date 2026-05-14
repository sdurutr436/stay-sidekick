"""Tests de integración para el blueprint del Vault de comunicaciones."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-vault"


def _token(rol: str = "operativo", empresa_id: str = "emp-1") -> str:
    payload = {
        "sub": "user@test.com",
        "user_id": "user-1",
        "empresa_id": empresa_id,
        "rol": rol,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.h_vault_comunicaciones.routes import h_vault_comunicaciones_bp
    from app.extensions import limiter

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(h_vault_comunicaciones_bp)
    return app.test_client()


def _auth(rol="operativo"):
    return {"Authorization": f"Bearer {_token(rol=rol)}"}


_PLANTILLA_DICT = {
    "id": "p-1",
    "nombre": "Bienvenida",
    "contenido": "Hola {NOMBRE}",
    "idioma": "es",
    "categoria": "BIENVENIDA",
    "activa": True,
    "empresa_id": "emp-1",
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-01-01T00:00:00",
}


# ── GET /api/vault/plantillas ──────────────────────────────────────────────


def test_list_plantillas_sin_token_devuelve_401(client):
    resp = client.get("/api/vault/plantillas")
    assert resp.status_code == 401


def test_list_plantillas_devuelve_200(client):
    with patch("app.h_vault_comunicaciones.routes.service.list_plantillas", return_value=[_PLANTILLA_DICT]):
        resp = client.get("/api/vault/plantillas", headers=_auth())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert len(data["plantillas"]) == 1
    assert data["plantillas"][0]["nombre"] == "Bienvenida"


# ── POST /api/vault/plantillas ─────────────────────────────────────────────


def test_crear_plantilla_sin_nombre_devuelve_422(client):
    resp = client.post("/api/vault/plantillas", headers=_auth(), json={"nombre": "", "contenido": "hola"})
    assert resp.status_code == 422
    assert resp.get_json()["errors"] == ["El nombre debe tener entre 1 y 200 caracteres."]


def test_crear_plantilla_exitosa_devuelve_201(client):
    with patch("app.h_vault_comunicaciones.routes.service.crear_plantilla", return_value=_PLANTILLA_DICT):
        resp = client.post(
            "/api/vault/plantillas",
            headers=_auth(),
            json={"nombre": "Bienvenida", "contenido": "Hola", "idioma": "es", "categoria": "BIENVENIDA"},
        )
    assert resp.status_code == 201
    assert resp.get_json()["ok"] is True


# ── PUT /api/vault/plantillas/<id> ─────────────────────────────────────────


def test_actualizar_plantilla_no_encontrada_devuelve_404(client):
    with patch("app.h_vault_comunicaciones.routes.service.actualizar_plantilla", return_value=(None, "Plantilla no encontrada.")):
        resp = client.put(
            "/api/vault/plantillas/00000000-0000-0000-0000-000000000000",
            headers=_auth(),
            json={"nombre": "X", "contenido": "Y"},
        )
    assert resp.status_code == 404


# ── POST /api/vault/plantillas/<id>/mejoras ────────────────────────────────


def test_mejorar_plantilla_no_encontrada_devuelve_404(client):
    with patch("app.h_vault_comunicaciones.routes.service.get_plantilla", return_value=None):
        resp = client.post(
            "/api/vault/plantillas/00000000-0000-0000-0000-000000000000/mejoras",
            headers=_auth(),
            json={"contenido": "hola", "idioma": "es"},
        )
    assert resp.status_code == 404


def test_mejorar_plantilla_exitosa_devuelve_200(client):
    with patch("app.h_vault_comunicaciones.routes.service.get_plantilla", return_value=_PLANTILLA_DICT), \
         patch("app.h_vault_comunicaciones.routes.ai_service.mejorar", return_value="texto mejorado"):
        resp = client.post(
            "/api/vault/plantillas/00000000-0000-0000-0000-000000000001/mejoras",
            headers=_auth(),
            json={"contenido": "hola", "idioma": "es"},
        )
    assert resp.status_code == 200
    assert resp.get_json()["contenido"] == "texto mejorado"


# ── POST /api/vault/plantillas/<id>/traducciones ───────────────────────────


def test_traducir_plantilla_exitosa_devuelve_200(client):
    with patch("app.h_vault_comunicaciones.routes.service.get_plantilla", return_value=_PLANTILLA_DICT), \
         patch("app.h_vault_comunicaciones.routes.ai_service.traducir", return_value="hello"):
        resp = client.post(
            "/api/vault/plantillas/00000000-0000-0000-0000-000000000001/traducciones",
            headers=_auth(),
            json={"contenido": "hola", "idioma_destino": "en"},
        )
    assert resp.status_code == 200
    assert resp.get_json()["contenido"] == "hello"


# ── GET /api/ai/config (solo admin) ───────────────────────────────────────


def test_ai_config_operativo_devuelve_403(client):
    resp = client.get("/api/ai/config", headers=_auth("operativo"))
    assert resp.status_code == 403
