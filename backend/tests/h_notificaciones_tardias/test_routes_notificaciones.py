"""Tests de integración para el blueprint de notificaciones de check-in tardío."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-notificaciones"


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


def _auth(rol: str = "operativo") -> dict:
    return {"Authorization": f"Bearer {_token(rol=rol)}"}


@pytest.fixture
def client():
    from app.extensions import limiter
    from app.h_notificaciones_tardias.routes import notificaciones_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    limiter.init_app(app)
    app.register_blueprint(notificaciones_bp)
    return app.test_client()


# ── GET /api/notificaciones/checkin-tardio/status ──────────────────────────


def test_status_sin_token_devuelve_401(client):
    resp = client.get("/api/notificaciones/checkin-tardio/status")
    assert resp.status_code == 401


def test_status_devuelve_200_con_payload(client):
    payload = {
        "mail_configurado": True,
        "pms_configurado": True,
        "pms_error": None,
        "apartamentos": [{"id": "a1", "nombre": "A1", "ciudad": "Cádiz"}],
        "reservas_pms": [],
        "hora_corte": "20:00",
    }
    with patch(
        "app.h_notificaciones_tardias.routes.service.get_status",
        return_value=payload,
    ):
        resp = client.get(
            "/api/notificaciones/checkin-tardio/status",
            headers=_auth(),
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["mail_configurado"] is True
    assert data["pms_configurado"] is True
    assert data["hora_corte"] == "20:00"


def test_status_acepta_param_fecha(client):
    payload = {
        "mail_configurado": False,
        "pms_configurado": False,
        "pms_error": None,
        "apartamentos": [],
        "reservas_pms": [],
        "hora_corte": "20:00",
    }
    with patch(
        "app.h_notificaciones_tardias.routes.service.get_status",
        return_value=payload,
    ) as mock_status:
        resp = client.get(
            "/api/notificaciones/checkin-tardio/status?fecha=2026-05-22",
            headers=_auth(),
        )
    assert resp.status_code == 200
    mock_status.assert_called_once_with("emp-1", fecha="2026-05-22")


# ── POST /api/notificaciones/checkin-tardio/checkins ──────────────────────


def test_upload_xlsx_sin_token_devuelve_401(client):
    resp = client.post("/api/notificaciones/checkin-tardio/checkins")
    assert resp.status_code == 401


def test_upload_xlsx_sin_campo_file_devuelve_400(client):
    resp = client.post(
        "/api/notificaciones/checkin-tardio/checkins",
        headers=_auth(),
        data={},
    )
    assert resp.status_code == 400
    assert "'file'" in resp.get_json()["errors"][0]


def test_upload_xlsx_extension_invalida_devuelve_400(client):
    data = {"file": (BytesIO(b"contenido"), "reservas.csv")}
    resp = client.post(
        "/api/notificaciones/checkin-tardio/checkins",
        headers=_auth(),
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert ".xlsx" in resp.get_json()["errors"][0]


def test_upload_xlsx_archivo_vacio_devuelve_400(client):
    data = {"file": (BytesIO(b""), "reservas.xlsx")}
    resp = client.post(
        "/api/notificaciones/checkin-tardio/checkins",
        headers=_auth(),
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert "vacío" in resp.get_json()["errors"][0]


def test_upload_xlsx_ok_devuelve_200(client):
    data = {"file": (BytesIO(b"binario-xlsx"), "reservas.xlsx")}
    checkins = [{"nombre": "Juan", "hora_llegada": "21:00"}]
    with patch(
        "app.h_notificaciones_tardias.routes.perfil_repo.get_notif_tardio_config",
        return_value={"hora_corte": "20:00"},
    ), patch(
        "app.h_notificaciones_tardias.routes.service.parse_checkins_xlsx",
        return_value=(checkins, []),
    ):
        resp = client.post(
            "/api/notificaciones/checkin-tardio/checkins",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["checkins"] == checkins
    assert "warnings" not in body


def test_upload_xlsx_devuelve_warnings_si_existen(client):
    data = {"file": (BytesIO(b"binario-xlsx"), "reservas.xlsx")}
    with patch(
        "app.h_notificaciones_tardias.routes.perfil_repo.get_notif_tardio_config",
        return_value={"hora_corte": "20:00"},
    ), patch(
        "app.h_notificaciones_tardias.routes.service.parse_checkins_xlsx",
        return_value=([], ["fila 3 sin nombre"]),
    ):
        resp = client.post(
            "/api/notificaciones/checkin-tardio/checkins",
            headers=_auth(),
            data=data,
            content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["warnings"] == ["fila 3 sin nombre"]


# ── Plantillas ────────────────────────────────────────────────────────────


def _build_plantilla_mock(plantilla_id="p-1", nombre="Aviso noche", contenido="Hola"):
    plantilla = MagicMock()
    plantilla.id = plantilla_id
    plantilla.nombre = nombre
    plantilla.contenido = contenido
    return plantilla


def _mock_query_for(model_mock, *, first=None, all_=None):
    """Configura la cadena .query.filter_by(...).order_by(...).{first,all}() sobre un mock de modelo."""
    chain = MagicMock()
    chain.filter_by.return_value = chain
    chain.order_by.return_value = chain
    chain.first.return_value = first
    chain.all.return_value = all_ if all_ is not None else []
    model_mock.query = chain
    return chain


def test_list_plantillas_sin_token_devuelve_401(client):
    resp = client.get("/api/notificaciones/checkin-tardio/plantillas")
    assert resp.status_code == 401


def test_list_plantillas_devuelve_200_con_lista(client):
    plantilla = _build_plantilla_mock()
    with patch(
        "app.h_notificaciones_tardias.routes.PlantillaVault"
    ) as model:
        _mock_query_for(model, all_=[plantilla])
        resp = client.get(
            "/api/notificaciones/checkin-tardio/plantillas",
            headers=_auth(),
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert len(body["plantillas"]) == 1
    assert body["plantillas"][0]["nombre"] == "Aviso noche"


def test_create_plantilla_sin_nombre_devuelve_400(client):
    resp = client.post(
        "/api/notificaciones/checkin-tardio/plantillas",
        headers=_auth(),
        json={"nombre": "", "contenido": "hola"},
    )
    assert resp.status_code == 400
    assert "nombre" in resp.get_json()["errors"][0].lower()


def test_create_plantilla_sin_contenido_devuelve_400(client):
    resp = client.post(
        "/api/notificaciones/checkin-tardio/plantillas",
        headers=_auth(),
        json={"nombre": "X", "contenido": ""},
    )
    assert resp.status_code == 400
    assert "contenido" in resp.get_json()["errors"][0].lower()


def test_create_plantilla_ok_devuelve_201(client):
    with patch(
        "app.h_notificaciones_tardias.routes.db.session"
    ) as mock_session:
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        resp = client.post(
            "/api/notificaciones/checkin-tardio/plantillas",
            headers=_auth(),
            json={"nombre": "Aviso", "contenido": "Buenas noches"},
        )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    assert body["plantilla"]["nombre"] == "Aviso"


def test_update_plantilla_sin_nombre_devuelve_400(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    resp = client.put(
        f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
        headers=_auth(),
        json={"nombre": "", "contenido": "x"},
    )
    assert resp.status_code == 400


def test_update_plantilla_sin_contenido_devuelve_400(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    resp = client.put(
        f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
        headers=_auth(),
        json={"nombre": "x", "contenido": ""},
    )
    assert resp.status_code == 400


def test_update_plantilla_no_existe_devuelve_404(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    with patch(
        "app.h_notificaciones_tardias.routes.PlantillaVault"
    ) as model:
        _mock_query_for(model, first=None)
        resp = client.put(
            f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
            headers=_auth(),
            json={"nombre": "X", "contenido": "Y"},
        )
    assert resp.status_code == 404


def test_update_plantilla_ok_devuelve_200(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    plantilla = _build_plantilla_mock(plantilla_id=plantilla_id, nombre="viejo", contenido="viejo")
    with patch(
        "app.h_notificaciones_tardias.routes.PlantillaVault"
    ) as model, patch(
        "app.h_notificaciones_tardias.routes.db.session"
    ):
        _mock_query_for(model, first=plantilla)
        resp = client.put(
            f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
            headers=_auth(),
            json={"nombre": "Nuevo", "contenido": "Nuevo contenido"},
        )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["plantilla"]["nombre"] == "Nuevo"


def test_delete_plantilla_no_existe_devuelve_404(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    with patch(
        "app.h_notificaciones_tardias.routes.PlantillaVault"
    ) as model:
        _mock_query_for(model, first=None)
        resp = client.delete(
            f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
            headers=_auth(),
        )
    assert resp.status_code == 404


def test_delete_plantilla_ok_devuelve_200(client):
    plantilla_id = "11111111-1111-1111-1111-111111111111"
    plantilla = _build_plantilla_mock(plantilla_id=plantilla_id)
    with patch(
        "app.h_notificaciones_tardias.routes.PlantillaVault"
    ) as model, patch(
        "app.h_notificaciones_tardias.routes.db.session"
    ):
        _mock_query_for(model, first=plantilla)
        resp = client.delete(
            f"/api/notificaciones/checkin-tardio/plantillas/{plantilla_id}",
            headers=_auth(),
        )
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
