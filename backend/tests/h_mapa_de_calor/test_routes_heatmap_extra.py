"""Tests adicionales del blueprint del mapa de calor (cubre rutas faltantes)."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-heatmap-extra"


def _token(rol="admin", empresa_id="emp-1"):
    payload = {
        "sub": "u@test.com",
        "user_id": "u-1",
        "empresa_id": empresa_id,
        "rol": rol,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm="HS256")


def _auth(rol="admin"):
    return {"Authorization": f"Bearer {_token(rol=rol)}"}


@pytest.fixture
def client():
    from app.extensions import limiter
    from app.h_mapa_de_calor.routes import heatmap_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(heatmap_bp)
    return app.test_client()


# ── Umbrales ──────────────────────────────────────────────────────────────


def test_get_umbrales_sin_token_devuelve_401(client):
    resp = client.get("/api/heatmap/umbrales")
    assert resp.status_code == 401


def test_get_umbrales_devuelve_200(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.get_umbrales",
        return_value={"nivel1": 1, "nivel2": 3, "nivel3": 5},
    ):
        resp = client.get("/api/heatmap/umbrales", headers=_auth())
    assert resp.status_code == 200


def test_save_umbrales_rol_operativo_devuelve_403(client):
    resp = client.put(
        "/api/heatmap/umbrales", headers=_auth(rol="operativo"),
        json={"nivel1": 1, "nivel2": 3, "nivel3": 5},
    )
    assert resp.status_code == 403


def test_save_umbrales_sin_body_devuelve_400(client):
    resp = client.put("/api/heatmap/umbrales", headers=_auth())
    assert resp.status_code == 400


def test_save_umbrales_validacion_falla_devuelve_422(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.save_umbrales",
        return_value=(None, ["umbrales malos"]),
    ):
        resp = client.put(
            "/api/heatmap/umbrales",
            headers=_auth(),
            json={"nivel1": 1, "nivel2": 1, "nivel3": 1},
        )
    assert resp.status_code == 422


def test_save_umbrales_ok_devuelve_200(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.save_umbrales",
        return_value=({"nivel1": 1, "nivel2": 3, "nivel3": 5}, []),
    ):
        resp = client.put(
            "/api/heatmap/umbrales",
            headers=_auth(),
            json={"nivel1": 1, "nivel2": 3, "nivel3": 5},
        )
    assert resp.status_code == 200


# ── Config XLSX ────────────────────────────────────────────────────────────


def test_get_config_xlsx_sin_token_401(client):
    resp = client.get("/api/heatmap/config-xlsx")
    assert resp.status_code == 401


def test_get_config_xlsx_ok(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.get_config_xlsx",
        return_value={"col_fecha_checkin": "B"},
    ):
        resp = client.get("/api/heatmap/config-xlsx", headers=_auth())
    assert resp.status_code == 200


def test_save_config_xlsx_rol_operativo_403(client):
    resp = client.put(
        "/api/heatmap/config-xlsx", headers=_auth(rol="operativo"),
        json={"col_fecha_checkin": "B"},
    )
    assert resp.status_code == 403


def test_save_config_xlsx_sin_body_400(client):
    resp = client.put("/api/heatmap/config-xlsx", headers=_auth())
    assert resp.status_code == 400


def test_save_config_xlsx_validacion_422(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.save_config_xlsx",
        return_value=(None, ["err"]),
    ):
        resp = client.put(
            "/api/heatmap/config-xlsx",
            headers=_auth(),
            json={"col_fecha_checkin": "999"},
        )
    assert resp.status_code == 422


def test_save_config_xlsx_ok(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.save_config_xlsx",
        return_value=({"col_fecha_checkin": "B"}, []),
    ):
        resp = client.put(
            "/api/heatmap/config-xlsx",
            headers=_auth(),
            json={"col_fecha_checkin": "B"},
        )
    assert resp.status_code == 200


# ── GET /api/heatmap (desde PMS) ──────────────────────────────────────────


def test_generar_desde_pms_sin_token_401(client):
    resp = client.get("/api/heatmap")
    assert resp.status_code == 401


def test_generar_desde_pms_sin_desde_devuelve_422(client):
    resp = client.get("/api/heatmap?hasta=2026-05-28", headers=_auth())
    assert resp.status_code == 422


def test_generar_desde_pms_sin_hasta_422(client):
    resp = client.get("/api/heatmap?desde=2026-05-22", headers=_auth())
    assert resp.status_code == 422


def test_generar_desde_pms_fecha_mal_formada_422(client):
    resp = client.get(
        "/api/heatmap?desde=2026/05/22&hasta=2026-05-28", headers=_auth()
    )
    assert resp.status_code == 422


def test_generar_desde_pms_rango_inverso_422(client):
    resp = client.get(
        "/api/heatmap?desde=2026-05-28&hasta=2026-05-22", headers=_auth()
    )
    assert resp.status_code == 422


def test_generar_desde_pms_servicio_error_400(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_pms",
        return_value=(None, "PMS no configurado"),
    ):
        resp = client.get(
            "/api/heatmap?desde=2026-05-22&hasta=2026-05-28", headers=_auth()
        )
    assert resp.status_code == 400


def test_generar_desde_pms_ok(client):
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_pms",
        return_value=([{"fecha": "2026-05-22", "checkins": 1, "checkouts": 0}], None),
    ):
        resp = client.get(
            "/api/heatmap?desde=2026-05-22&hasta=2026-05-28", headers=_auth()
        )
    assert resp.status_code == 200


# ── POST /api/heatmap/xlsx ────────────────────────────────────────────────


def test_generar_desde_xlsx_sin_token_401(client):
    resp = client.post("/api/heatmap/xlsx")
    assert resp.status_code == 401


def test_generar_desde_xlsx_sin_archivo_400(client):
    resp = client.post(
        "/api/heatmap/xlsx",
        headers=_auth(),
        data={"desde": "2026-05-22", "hasta": "2026-05-28"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_generar_desde_xlsx_fecha_invalida_422(client):
    data = {"checkins": (BytesIO(b"x"), "ci.xlsx"), "desde": "mala", "hasta": "2026-05-28"}
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 422


def test_generar_desde_xlsx_rango_inverso_422(client):
    data = {"checkins": (BytesIO(b"x"), "ci.xlsx"), "desde": "2026-05-28", "hasta": "2026-05-22"}
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 422


def test_generar_desde_xlsx_extension_invalida_400(client):
    data = {"checkins": (BytesIO(b"x"), "ci.csv"), "desde": "2026-05-22", "hasta": "2026-05-28"}
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_generar_desde_xlsx_vacio_400(client):
    data = {"checkins": (BytesIO(b""), "ci.xlsx"), "desde": "2026-05-22", "hasta": "2026-05-28"}
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_generar_desde_xlsx_checkouts_extension_mala_400(client):
    data = {
        "checkins": (BytesIO(b"x"), "ci.xlsx"),
        "checkouts": (BytesIO(b"x"), "co.csv"),
        "desde": "2026-05-22",
        "hasta": "2026-05-28",
    }
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_generar_desde_xlsx_checkouts_vacio_400(client):
    data = {
        "checkins": (BytesIO(b"x"), "ci.xlsx"),
        "checkouts": (BytesIO(b""), "co.xlsx"),
        "desde": "2026-05-22",
        "hasta": "2026-05-28",
    }
    resp = client.post(
        "/api/heatmap/xlsx", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_generar_desde_xlsx_servicio_error_422(client):
    data = {"checkins": (BytesIO(b"x"), "ci.xlsx"), "desde": "2026-05-22", "hasta": "2026-05-28"}
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_xlsx",
        return_value=(None, [], "configura columna"),
    ):
        resp = client.post(
            "/api/heatmap/xlsx", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 422


def test_generar_desde_xlsx_ok(client):
    data = {"checkins": (BytesIO(b"x"), "ci.xlsx"), "desde": "2026-05-22", "hasta": "2026-05-28"}
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_xlsx",
        return_value=([{"fecha": "2026-05-22", "checkins": 1, "checkouts": 0}], [], None),
    ):
        resp = client.post(
            "/api/heatmap/xlsx", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 200


def test_generar_desde_xlsx_ok_con_warnings(client):
    data = {"checkins": (BytesIO(b"x"), "ci.xlsx"), "desde": "2026-05-22", "hasta": "2026-05-28"}
    with patch(
        "app.h_mapa_de_calor.routes.service.generar_desde_xlsx",
        return_value=([], ["2 filas descartadas"], None),
    ):
        resp = client.post(
            "/api/heatmap/xlsx", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    assert "warnings" in resp.get_json()
