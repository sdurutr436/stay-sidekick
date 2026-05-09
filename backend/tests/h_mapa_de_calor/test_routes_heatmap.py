"""Tests unitarios para las rutas GET /api/heatmap del mapa de calor."""

from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-para-tests"


def _token(empresa_id: str = "empresa_test") -> str:
    payload = {
        "sub": "test@test.com",
        "empresa_id": empresa_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def client():
    from app.h_mapa_de_calor.routes import heatmap_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.register_blueprint(heatmap_bp)
    return app.test_client()


def test_generar_pms_fecha_pasada_devuelve_200(client):
    """Fechas anteriores a hoy deben llegar al servicio sin devolver 422."""
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_pms",
        return_value=([], None),
    ):
        resp = client.get(
            "/api/heatmap?desde=2026-05-01&hasta=2026-05-31",
            headers={"Authorization": f"Bearer {_token()}"},
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True


def test_generar_pms_desde_mayor_que_hasta_devuelve_422(client):
    """La validación desde > hasta debe mantenerse y devolver 422."""
    resp = client.get(
        "/api/heatmap?desde=2026-05-30&hasta=2026-05-01",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["ok"] is False
    assert "'desde' debe ser anterior o igual a 'hasta'." in data["errors"]
