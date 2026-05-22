"""Tests adicionales del blueprint de apartamentos (cubre rutas faltantes)."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import patch

import jwt
import pytest
from flask import Flask

_JWT_SECRET = "test-secret-apts-extra"


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
    from app.h_maestro_apartamentos.routes import apartamentos_bp

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = _JWT_SECRET
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    limiter.init_app(app)
    app.register_blueprint(apartamentos_bp)
    return app.test_client()


_APT_DICT = {
    "id": "apt-1", "empresa_id": "emp-1", "id_pms": "1001",
    "id_externo": "{1001}", "nombre": "A1", "direccion": "D1", "ciudad": "C",
    "pms_origen": "manual", "activo": True,
    "created_at": "2026-05-01T00:00:00", "updated_at": "2026-05-01T00:00:00",
}


# ── CRUD ──────────────────────────────────────────────────────────────────


def test_list_apartamentos_sin_token_401(client):
    resp = client.get("/api/apartamentos")
    assert resp.status_code == 401


def test_list_apartamentos_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.list_apartamentos",
        return_value=[_APT_DICT],
    ):
        resp = client.get("/api/apartamentos", headers=_auth())
    assert resp.status_code == 200
    assert len(resp.get_json()["apartamentos"]) == 1


def test_get_apartamento_no_encontrado_404(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.get_apartamento",
        return_value=(None, "Apartamento no encontrado."),
    ):
        resp = client.get("/api/apartamentos/x", headers=_auth())
    assert resp.status_code == 404


def test_get_apartamento_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.get_apartamento",
        return_value=(_APT_DICT, None),
    ):
        resp = client.get("/api/apartamentos/apt-1", headers=_auth())
    assert resp.status_code == 200


def test_create_apartamento_sin_body_400(client):
    resp = client.post("/api/apartamentos", headers=_auth())
    assert resp.status_code == 400


def test_create_apartamento_validacion_422(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.create_apartamento",
        return_value=(None, ["nombre obligatorio"]),
    ):
        resp = client.post(
            "/api/apartamentos", headers=_auth(),
            json={"nombre": ""},
        )
    assert resp.status_code == 422


def test_create_apartamento_ok_201(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.create_apartamento",
        return_value=(_APT_DICT, []),
    ):
        resp = client.post(
            "/api/apartamentos", headers=_auth(),
            json={"nombre": "A1"},
        )
    assert resp.status_code == 201


def test_update_apartamento_sin_body_400(client):
    resp = client.put("/api/apartamentos/x", headers=_auth())
    assert resp.status_code == 400


def test_update_apartamento_no_encontrado_404(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.update_apartamento",
        return_value=(None, ["Apartamento no encontrado."]),
    ):
        resp = client.put(
            "/api/apartamentos/x", headers=_auth(), json={"nombre": "X"}
        )
    assert resp.status_code == 404


def test_update_apartamento_validacion_422(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.update_apartamento",
        return_value=(None, ["nombre demasiado largo"]),
    ):
        resp = client.put(
            "/api/apartamentos/apt-1", headers=_auth(), json={"nombre": "x"*1000}
        )
    assert resp.status_code == 422


def test_update_apartamento_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.update_apartamento",
        return_value=(_APT_DICT, []),
    ):
        resp = client.put(
            "/api/apartamentos/apt-1", headers=_auth(), json={"nombre": "Nuevo"}
        )
    assert resp.status_code == 200


def test_delete_apartamento_no_encontrado_404(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.delete_apartamento",
        return_value="Apartamento no encontrado.",
    ):
        resp = client.delete("/api/apartamentos/x", headers=_auth())
    assert resp.status_code == 404


def test_delete_apartamento_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.delete_apartamento",
        return_value=None,
    ):
        resp = client.delete("/api/apartamentos/apt-1", headers=_auth())
    assert resp.status_code == 200


# ── Sincronización Smoobu ────────────────────────────────────────────────


def test_sync_smoobu_sin_token_401(client):
    resp = client.post("/api/apartamentos/sincronizacion/smoobu")
    assert resp.status_code == 401


def test_sync_smoobu_error_400(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.sync_from_smoobu",
        return_value=(None, "PMS no configurado"),
    ):
        resp = client.post(
            "/api/apartamentos/sincronizacion/smoobu", headers=_auth()
        )
    assert resp.status_code == 400


def test_sync_smoobu_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.sync_from_smoobu",
        return_value=({"nuevos": 1, "actualizados": 0}, None),
    ):
        resp = client.post(
            "/api/apartamentos/sincronizacion/smoobu", headers=_auth()
        )
    assert resp.status_code == 200


# ── Importación XLSX ─────────────────────────────────────────────────────


def test_import_xlsx_sin_archivo_400(client):
    resp = client.post(
        "/api/apartamentos/importacion", headers=_auth(),
        data={}, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_import_xlsx_extension_invalida_400(client):
    data = {"file": (BytesIO(b"x"), "f.csv")}
    resp = client.post(
        "/api/apartamentos/importacion", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_import_xlsx_vacio_400(client):
    data = {"file": (BytesIO(b""), "f.xlsx")}
    resp = client.post(
        "/api/apartamentos/importacion", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_import_xlsx_error_servicio_422(client):
    data = {"file": (BytesIO(b"x"), "f.xlsx")}
    with patch(
        "app.h_maestro_apartamentos.routes.service.import_from_xlsx",
        return_value=(None, ["parse error"]),
    ):
        resp = client.post(
            "/api/apartamentos/importacion", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 422


def test_import_xlsx_ok(client):
    data = {"file": (BytesIO(b"x"), "f.xlsx")}
    with patch(
        "app.h_maestro_apartamentos.routes.service.import_from_xlsx",
        return_value=({"nuevos": 2}, []),
    ):
        resp = client.post(
            "/api/apartamentos/importacion", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 200


def test_import_xlsx_ok_con_warnings(client):
    data = {"file": (BytesIO(b"x"), "f.xlsx")}
    with patch(
        "app.h_maestro_apartamentos.routes.service.import_from_xlsx",
        return_value=({"nuevos": 1}, ["fila 3 mal"]),
    ):
        resp = client.post(
            "/api/apartamentos/importacion", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 200
    assert "warnings" in resp.get_json()


# ── Preview ──────────────────────────────────────────────────────────────


def test_preview_sin_archivo_400(client):
    resp = client.post(
        "/api/apartamentos/importacion/preview", headers=_auth(),
        data={}, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_preview_extension_invalida_400(client):
    data = {"file": (BytesIO(b"x"), "f.csv")}
    resp = client.post(
        "/api/apartamentos/importacion/preview", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_preview_vacio_400(client):
    data = {"file": (BytesIO(b""), "f.xlsx")}
    resp = client.post(
        "/api/apartamentos/importacion/preview", headers=_auth(),
        data=data, content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_preview_ok(client):
    data = {"file": (BytesIO(b"x"), "f.xlsx")}
    with patch(
        "app.h_maestro_apartamentos.routes.service.preview_import_xlsx",
        return_value=({"nuevos": [], "actualizados": [], "sin_cambios": [], "errores": []}, []),
    ):
        resp = client.post(
            "/api/apartamentos/importacion/preview", headers=_auth(),
            data=data, content_type="multipart/form-data",
        )
    assert resp.status_code == 200


# ── PMS config ────────────────────────────────────────────────────────────


def test_get_pms_config_none_devuelve_200(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.get_pms_config",
        return_value=None,
    ):
        resp = client.get("/api/apartamentos/pms", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["config"] is None


def test_get_pms_config_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.get_pms_config",
        return_value={"proveedor": "smoobu"},
    ):
        resp = client.get("/api/apartamentos/pms", headers=_auth())
    assert resp.status_code == 200
    assert resp.get_json()["config"]["proveedor"] == "smoobu"


def test_save_pms_config_sin_body_400(client):
    resp = client.put("/api/apartamentos/pms", headers=_auth())
    assert resp.status_code == 400


def test_save_pms_config_validacion_422(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.save_pms_config",
        return_value=(None, ["err"]),
    ):
        resp = client.put(
            "/api/apartamentos/pms", headers=_auth(),
            json={"proveedor": ""},
        )
    assert resp.status_code == 422


def test_save_pms_config_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.save_pms_config",
        return_value=({"proveedor": "smoobu"}, []),
    ):
        resp = client.put(
            "/api/apartamentos/pms", headers=_auth(),
            json={"proveedor": "smoobu", "api_key": "k" * 20},
        )
    assert resp.status_code == 200


def test_delete_pms_config_no_existe_404(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.delete_pms_config",
        return_value="No hay configuración PMS para eliminar.",
    ):
        resp = client.delete("/api/apartamentos/pms", headers=_auth())
    assert resp.status_code == 404


def test_delete_pms_config_ok(client):
    with patch(
        "app.h_maestro_apartamentos.routes.service.delete_pms_config",
        return_value=None,
    ):
        resp = client.delete("/api/apartamentos/pms", headers=_auth())
    assert resp.status_code == 200
