"""Tests de integración para el blueprint del sincronizador de contactos."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-contactos"


def _token(rol: str = "admin", empresa_id: str = "emp-1") -> str:
    payload = {
        "sub": "user@test.com",
        "user_id": "user-1",
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
    from app.h_sincronizador_contactos.routes import contactos_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.config["FRONTEND_BASE_URL"] = "http://localhost:4200"
    limiter.init_app(app)
    app.register_blueprint(contactos_bp)
    return app.test_client()


# ── OAuth auth URL ─────────────────────────────────────────────────────────


def test_google_auth_sin_token_devuelve_401(client):
    resp = client.get("/api/contactos/google/auth")
    assert resp.status_code == 401


def test_google_auth_rol_operativo_devuelve_403(client):
    resp = client.get("/api/contactos/google/auth", headers=_auth(rol="operativo"))
    assert resp.status_code == 403


def test_google_auth_ok_devuelve_url(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.build_oauth_url",
        return_value="https://accounts.google.com/oauth?state=xyz",
    ):
        resp = client.get("/api/contactos/google/auth", headers=_auth())
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["url"].startswith("https://")


# ── OAuth callback ─────────────────────────────────────────────────────────


def test_google_callback_error_redirige_a_acceso_denegado(client):
    resp = client.get("/api/contactos/google/callback?error=access_denied")
    assert resp.status_code == 302
    assert "google_error=acceso_denegado" in resp.headers["Location"]


def test_google_callback_sin_state_redirige_estado_invalido(client):
    resp = client.get("/api/contactos/google/callback?code=abc")
    assert resp.status_code == 302
    assert "google_error=estado_invalido" in resp.headers["Location"]


def test_google_callback_state_invalido_redirige(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.verify_oauth_state",
        return_value=None,
    ):
        resp = client.get("/api/contactos/google/callback?code=abc&state=mal")
    assert resp.status_code == 302
    assert "google_error=estado_invalido" in resp.headers["Location"]


def test_google_callback_sin_code_redirige_codigo_invalido(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.verify_oauth_state",
        return_value="emp-1",
    ):
        resp = client.get("/api/contactos/google/callback?state=xyz")
    assert resp.status_code == 302
    assert "google_error=codigo_invalido" in resp.headers["Location"]


def test_google_callback_token_fallido_redirige(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.verify_oauth_state",
        return_value="emp-1",
    ), patch(
        "app.h_sincronizador_contactos.routes.service.exchange_code_for_tokens",
        return_value=(False, "auth-error"),
    ):
        resp = client.get(
            "/api/contactos/google/callback?code=abc&state=xyz"
        )
    assert resp.status_code == 302
    assert "google_error=token_fallido" in resp.headers["Location"]


def test_google_callback_ok_redirige_a_conectado(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.verify_oauth_state",
        return_value="emp-1",
    ), patch(
        "app.h_sincronizador_contactos.routes.service.exchange_code_for_tokens",
        return_value=(True, None),
    ):
        resp = client.get(
            "/api/contactos/google/callback?code=abc&state=xyz"
        )
    assert resp.status_code == 302
    assert "google_conectado=true" in resp.headers["Location"]


# ── Status / disconnect ────────────────────────────────────────────────────


def test_google_status_sin_token_devuelve_401(client):
    resp = client.get("/api/contactos/google/status")
    assert resp.status_code == 401


def test_google_status_ok_devuelve_200(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.get_google_status",
        return_value={"conectado": True, "scope": "contacts"},
    ):
        resp = client.get("/api/contactos/google/status", headers=_auth())
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["google"]["conectado"] is True


def test_google_disconnect_rol_operativo_devuelve_403(client):
    resp = client.delete(
        "/api/contactos/google/conexion", headers=_auth(rol="operativo")
    )
    assert resp.status_code == 403


def test_google_disconnect_no_existe_devuelve_404(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.disconnect_google",
        return_value="no conectado",
    ):
        resp = client.delete("/api/contactos/google/conexion", headers=_auth())
    assert resp.status_code == 404


def test_google_disconnect_ok_devuelve_200(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.disconnect_google",
        return_value=None,
    ):
        resp = client.delete("/api/contactos/google/conexion", headers=_auth())
    assert resp.status_code == 200


# ── Preferencias ─────────────────────────────────────────────────────────


def test_get_preferencias_sin_token_devuelve_401(client):
    resp = client.get("/api/contactos/preferencias")
    assert resp.status_code == 401


def test_get_preferencias_devuelve_200(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.get_preferencias",
        return_value={"formato_nombre": "apellido_nombre"},
    ):
        resp = client.get("/api/contactos/preferencias", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["preferencias"]["formato_nombre"] == "apellido_nombre"


def test_save_preferencias_sin_body_devuelve_400(client):
    resp = client.put("/api/contactos/preferencias", headers=_auth())
    assert resp.status_code == 400


def test_save_preferencias_validacion_devuelve_422(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.save_preferencias",
        return_value=(None, ["formato_nombre inválido"]),
    ):
        resp = client.put(
            "/api/contactos/preferencias",
            headers=_auth(),
            json={"formato_nombre": "xxx"},
        )
    assert resp.status_code == 422


def test_save_preferencias_ok_devuelve_200(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.save_preferencias",
        return_value=({"formato_nombre": "apellido_nombre"}, []),
    ):
        resp = client.put(
            "/api/contactos/preferencias",
            headers=_auth(),
            json={"formato_nombre": "apellido_nombre"},
        )
    assert resp.status_code == 200


# ── Sincronización PMS → Google ───────────────────────────────────────────


def test_sync_contacts_sin_token_devuelve_401(client):
    resp = client.post("/api/contactos/sincronizacion")
    assert resp.status_code == 401


def test_sync_contacts_error_devuelve_400(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.sync_contacts",
        return_value=(None, "google no conectado"),
    ):
        resp = client.post(
            "/api/contactos/sincronizacion",
            headers=_auth(),
            json={"desde": "2026-05-01", "hasta": "2026-05-31"},
        )
    assert resp.status_code == 400


def test_sync_contacts_ok_devuelve_200(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.sync_contacts",
        return_value=({"creados": 3, "actualizados": 1}, None),
    ):
        resp = client.post(
            "/api/contactos/sincronizacion",
            headers=_auth(),
            json={"desde": "2026-05-01", "hasta": "2026-05-31"},
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["resultado"]["creados"] == 3


# ── Export CSV PMS ─────────────────────────────────────────────────────────


def test_export_csv_sin_token_devuelve_401(client):
    resp = client.post("/api/contactos/exportacion/csv")
    assert resp.status_code == 401


def test_export_csv_error_devuelve_400(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.export_csv",
        return_value=(None, "PMS no configurado"),
    ):
        resp = client.post(
            "/api/contactos/exportacion/csv",
            headers=_auth(),
            json={"desde": "2026-05-01"},
        )
    assert resp.status_code == 400


def test_export_csv_ok_devuelve_csv(client):
    with patch(
        "app.h_sincronizador_contactos.routes.service.export_csv",
        return_value=(b"Name,Phone\nJuan,600\n", None),
    ):
        resp = client.post(
            "/api/contactos/exportacion/csv",
            headers=_auth(),
            json={"desde": "2026-05-01", "hasta": "2026-05-31"},
        )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["Content-Type"]
    assert b"Juan" in resp.data


# ── XLSX sync ──────────────────────────────────────────────────────────────


def test_xlsx_sync_sin_token_devuelve_401(client):
    resp = client.post("/api/contactos/xlsx/sincronizacion")
    assert resp.status_code == 401


def test_xlsx_sync_sin_file_devuelve_400(client):
    resp = client.post(
        "/api/contactos/xlsx/sincronizacion",
        headers=_auth(),
        data={},
    )
    assert resp.status_code == 400


def test_xlsx_sync_extension_invalida_devuelve_400(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.csv")}
    resp = client.post(
        "/api/contactos/xlsx/sincronizacion",
        headers=_auth(),
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_xlsx_sync_error_servicio_devuelve_400(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.xlsx")}
    with patch(
        "app.h_sincronizador_contactos.routes.service.sync_from_xlsx",
        return_value=(None, "no se pudo leer xlsx"),
    ):
        resp = client.post(
            "/api/contactos/xlsx/sincronizacion",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 400


def test_xlsx_sync_ok_devuelve_200(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.xlsx")}
    with patch(
        "app.h_sincronizador_contactos.routes.service.sync_from_xlsx",
        return_value=({"creados": 5}, None),
    ):
        resp = client.post(
            "/api/contactos/xlsx/sincronizacion",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    assert resp.get_json()["resultado"]["creados"] == 5


# ── XLSX export CSV ────────────────────────────────────────────────────────


def test_xlsx_export_csv_sin_file_devuelve_400(client):
    resp = client.post(
        "/api/contactos/xlsx/exportacion/csv",
        headers=_auth(),
        data={},
    )
    assert resp.status_code == 400


def test_xlsx_export_csv_extension_invalida_devuelve_400(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.csv")}
    resp = client.post(
        "/api/contactos/xlsx/exportacion/csv",
        headers=_auth(),
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_xlsx_export_csv_error_servicio_devuelve_400(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.xlsx")}
    with patch(
        "app.h_sincronizador_contactos.routes.service.export_csv_from_xlsx",
        return_value=(None, "xlsx malformado"),
    ):
        resp = client.post(
            "/api/contactos/xlsx/exportacion/csv",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 400


def test_xlsx_export_csv_ok_devuelve_csv(client):
    data = {"file": (BytesIO(b"xxx"), "reservas.xlsx")}
    with patch(
        "app.h_sincronizador_contactos.routes.service.export_csv_from_xlsx",
        return_value=(b"Name,Phone\nA,1\n", None),
    ):
        resp = client.post(
            "/api/contactos/xlsx/exportacion/csv",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    assert b"Name" in resp.data
