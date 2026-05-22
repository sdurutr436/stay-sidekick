"""Tests unitarios del servicio de maestro de apartamentos."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from app.h_maestro_apartamentos import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        yield app


def _apartamento_mock(**overrides):
    apt = MagicMock()
    apt.id = "apt-1"
    apt.empresa_id = "emp-1"
    apt.id_pms = "1001"
    apt.id_externo = "{1001}"
    apt.nombre = "Apt"
    apt.direccion = "Calle 1"
    apt.ciudad = "Cádiz"
    apt.pms_origen = "manual"
    apt.activo = True
    apt.created_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    apt.updated_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    for k, v in overrides.items():
        setattr(apt, k, v)
    return apt


# ── _apt_to_dict ──────────────────────────────────────────────────────────


def test_apt_to_dict_serializa_campos():
    apt = _apartamento_mock()
    d = srv._apt_to_dict(apt)
    assert d["nombre"] == "Apt"
    assert d["activo"] is True
    assert d["created_at"] == "2026-05-01T00:00:00+00:00"


def test_apt_to_dict_fechas_none_no_explota():
    apt = _apartamento_mock()
    apt.created_at = None
    apt.updated_at = None
    d = srv._apt_to_dict(apt)
    assert d["created_at"] is None
    assert d["updated_at"] is None


# ── list / get ────────────────────────────────────────────────────────────


def test_list_apartamentos_devuelve_lista(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.list_by_empresa",
        return_value=[apt, apt],
    ):
        data = srv.list_apartamentos("emp-1")
    assert len(data) == 2


def test_get_apartamento_no_existe(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=None,
    ):
        data, err = srv.get_apartamento("emp-1", "no-existe")
    assert data is None
    assert err == "Apartamento no encontrado."


def test_get_apartamento_ok(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=apt,
    ):
        data, err = srv.get_apartamento("emp-1", "apt-1")
    assert err is None
    assert data["nombre"] == "Apt"


# ── create ────────────────────────────────────────────────────────────────


def test_create_apartamento_validacion_falla(app_ctx):
    data, errors = srv.create_apartamento("emp-1", {"nombre": ""})
    assert data is None
    assert errors


def test_create_apartamento_ok(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.create",
        return_value=apt,
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, errors = srv.create_apartamento("emp-1", {"nombre": "Apt"})
    assert errors == []
    assert data["nombre"] == "Apt"


# ── update ────────────────────────────────────────────────────────────────


def test_update_apartamento_no_existe(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=None,
    ):
        data, errors = srv.update_apartamento("emp-1", "x", {"nombre": "X"})
    assert data is None
    assert "no encontrado" in errors[0].lower()


def test_update_apartamento_validacion_falla(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=apt,
    ):
        # nombre demasiado largo (>255)
        data, errors = srv.update_apartamento(
            "emp-1", "apt-1", {"nombre": "x" * 500}
        )
    assert data is None
    assert errors


def test_update_apartamento_ok(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=apt,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.update"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, errors = srv.update_apartamento(
            "emp-1", "apt-1", {"nombre": "Nuevo"}
        )
    assert errors == []


# ── delete ────────────────────────────────────────────────────────────────


def test_delete_apartamento_no_existe(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=None,
    ):
        err = srv.delete_apartamento("emp-1", "x")
    assert "no encontrado" in err.lower()


def test_delete_apartamento_ok(app_ctx):
    apt = _apartamento_mock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id",
        return_value=apt,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.soft_delete"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        err = srv.delete_apartamento("emp-1", "apt-1")
    assert err is None


# ── sync_from_smoobu ──────────────────────────────────────────────────────


def test_sync_from_smoobu_sin_config(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=None,
    ):
        data, err = srv.sync_from_smoobu("emp-1")
    assert data is None
    assert "PMS" in err


def test_sync_from_smoobu_proveedor_distinto(app_ctx):
    config = MagicMock()
    config.api_key_cifrada = b"k"
    config.proveedor = "beds24"
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=config,
    ):
        data, err = srv.sync_from_smoobu("emp-1")
    assert data is None
    assert "smoobu" in err.lower()


def test_sync_from_smoobu_decrypt_falla(app_ctx):
    config = MagicMock()
    config.api_key_cifrada = b"k"
    config.proveedor = "smoobu"
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=config,
    ), patch(
        "app.h_maestro_apartamentos.service.decrypt",
        return_value=None,
    ):
        data, err = srv.sync_from_smoobu("emp-1")
    assert data is None
    assert "descifrar" in err.lower()


def test_sync_from_smoobu_error_externo(app_ctx):
    config = MagicMock()
    config.api_key_cifrada = b"k"
    config.proveedor = "smoobu"
    client = MagicMock()
    client.fetch_all_normalized.side_effect = requests.RequestException("boom")
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=config,
    ), patch(
        "app.h_maestro_apartamentos.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_maestro_apartamentos.service.SmoobuClient",
        return_value=client,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.create_sync_log"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, err = srv.sync_from_smoobu("emp-1")
    assert data is None
    assert "Smoobu" in err


def test_sync_from_smoobu_ok(app_ctx):
    config = MagicMock()
    config.api_key_cifrada = b"k"
    config.proveedor = "smoobu"
    apartamento_ext = MagicMock()
    apartamento_ext.id_externo = "1001"
    apartamento_ext.nombre = "A1"
    apartamento_ext.direccion = "D1"
    apartamento_ext.ciudad = "Cádiz"
    client = MagicMock()
    client.fetch_all_normalized.return_value = [apartamento_ext, apartamento_ext]
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=config,
    ), patch(
        "app.h_maestro_apartamentos.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_maestro_apartamentos.service.SmoobuClient",
        return_value=client,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.upsert_from_external",
        side_effect=[(None, True), (None, False)],
    ), patch(
        "app.h_maestro_apartamentos.service.repo.create_sync_log"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, err = srv.sync_from_smoobu("emp-1")
    assert err is None
    assert data["nuevos"] == 1
    assert data["actualizados"] == 1


# ── import_from_xlsx ──────────────────────────────────────────────────────


def test_import_from_xlsx_parse_error(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.parse_xlsx",
        return_value=([], ["error parseo"]),
    ), patch(
        "app.h_maestro_apartamentos.service._get_xlsx_col_override",
        return_value=None,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.create_sync_log"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, errors = srv.import_from_xlsx("emp-1", b"x")
    assert data is None
    assert errors == ["error parseo"]


def test_import_from_xlsx_ok(app_ctx):
    apt = MagicMock()
    apt.id_pms = "1001"
    apt.id_externo = "{1001}"
    apt.nombre = "A1"
    apt.direccion = "D"
    apt.ciudad = "Cádiz"
    with patch(
        "app.h_maestro_apartamentos.service.parse_xlsx",
        return_value=([apt, apt], []),
    ), patch(
        "app.h_maestro_apartamentos.service._get_xlsx_col_override",
        return_value=None,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.upsert_from_external",
        side_effect=[(None, True), (None, False)],
    ), patch(
        "app.h_maestro_apartamentos.service.repo.create_sync_log"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, errors = srv.import_from_xlsx("emp-1", b"x")
    assert errors == []
    assert data["nuevos"] == 1
    assert data["actualizados"] == 1


def test_import_from_xlsx_id_pms_fallback_a_externo(app_ctx):
    apt = MagicMock()
    apt.id_pms = None  # fuerza fallback
    apt.id_externo = "ext-9"
    apt.nombre = "A1"
    apt.direccion = None
    apt.ciudad = None
    with patch(
        "app.h_maestro_apartamentos.service.parse_xlsx",
        return_value=([apt], []),
    ), patch(
        "app.h_maestro_apartamentos.service._get_xlsx_col_override",
        return_value=None,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.upsert_from_external",
        return_value=(None, True),
    ) as upsert, patch(
        "app.h_maestro_apartamentos.service.repo.create_sync_log"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        srv.import_from_xlsx("emp-1", b"x")
    args, kwargs = upsert.call_args
    assert kwargs["id_pms"] == "ext-9"


# ── preview_import_xlsx ───────────────────────────────────────────────────


def test_preview_import_xlsx_separa_nuevos_actualizados_sin_cambios(app_ctx):
    apt_nuevo = MagicMock(id_pms="N", id_externo="{N}", nombre="Nuevo",
                          direccion="D", ciudad="C")
    apt_cambia = MagicMock(id_pms="C", id_externo="{C}", nombre="Cambia",
                           direccion="D2", ciudad="C2")
    apt_igual = MagicMock(id_pms="I", id_externo="{I}", nombre="Igual",
                          direccion=None, ciudad=None)

    existing_cambia = MagicMock(nombre="Antiguo")
    existing_igual = MagicMock(nombre="Igual", direccion="D", ciudad="C")

    def get_by_id_pms(_emp, id_pms):
        return {"N": None, "C": existing_cambia, "I": existing_igual}[id_pms]

    with patch(
        "app.h_maestro_apartamentos.service.parse_xlsx",
        return_value=([apt_nuevo, apt_cambia, apt_igual], []),
    ), patch(
        "app.h_maestro_apartamentos.service._get_xlsx_col_override",
        return_value=None,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.get_by_id_pms",
        side_effect=get_by_id_pms,
    ):
        data, _ = srv.preview_import_xlsx("emp-1", b"x")
    assert len(data["nuevos"]) == 1
    assert len(data["actualizados"]) == 1
    assert len(data["sin_cambios"]) == 1


# ── PMS config CRUD ───────────────────────────────────────────────────────


def test_save_pms_config_validacion_falla(app_ctx):
    data, errors = srv.save_pms_config("emp-1", {})
    assert data is None
    assert errors


def test_save_pms_config_ok(app_ctx):
    config = MagicMock(
        proveedor="smoobu",
        endpoint=None,
        activo=True,
        ultimo_sync=None,
    )
    with patch(
        "app.h_maestro_apartamentos.service.encrypt",
        return_value=b"cipher",
    ), patch(
        "app.h_maestro_apartamentos.service.repo.upsert_pms_config",
        return_value=config,
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        data, errors = srv.save_pms_config(
            "emp-1",
            {"proveedor": "smoobu", "api_key": "x" * 20},
        )
    assert errors == []
    assert data["proveedor"] == "smoobu"


def test_get_pms_config_none(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=None,
    ):
        data = srv.get_pms_config("emp-1")
    assert data is None


def test_get_pms_config_ok(app_ctx):
    cfg = MagicMock(
        proveedor="smoobu",
        endpoint="https://x.com",
        activo=True,
        ultimo_sync=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=cfg,
    ):
        data = srv.get_pms_config("emp-1")
    assert data["proveedor"] == "smoobu"
    assert "2026-05-01" in data["ultimo_sync"]


def test_delete_pms_config_no_existe(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=None,
    ):
        err = srv.delete_pms_config("emp-1")
    assert err is not None


def test_delete_pms_config_ok(app_ctx):
    cfg = MagicMock()
    with patch(
        "app.h_maestro_apartamentos.service.repo.get_pms_config",
        return_value=cfg,
    ), patch(
        "app.h_maestro_apartamentos.service.repo.delete_pms_config"
    ), patch(
        "app.h_maestro_apartamentos.service.db.session"
    ):
        err = srv.delete_pms_config("emp-1")
    assert err is None


# ── _get_xlsx_col_override ────────────────────────────────────────────────


def test_get_xlsx_col_override_sin_empresa(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.service.Empresa"
    ) as Emp:
        chain = MagicMock()
        chain.filter_by.return_value = chain
        chain.first.return_value = None
        Emp.query = chain
        result = srv._get_xlsx_col_override("emp-X")
    assert result is None


def test_get_xlsx_col_override_sin_columnas_validas(app_ctx):
    empresa = MagicMock()
    empresa.configuracion = {"xlsx_apartamentos": {"col_id_externo": 0, "col_nombre": 0}}
    with patch(
        "app.h_maestro_apartamentos.service.Empresa"
    ) as Emp:
        chain = MagicMock()
        chain.filter_by.return_value = chain
        chain.first.return_value = empresa
        Emp.query = chain
        result = srv._get_xlsx_col_override("emp-1")
    assert result is None


def test_get_xlsx_col_override_columnas_validas(app_ctx):
    empresa = MagicMock()
    empresa.configuracion = {"xlsx_apartamentos": {"col_id_externo": 1, "col_nombre": 2}}
    with patch(
        "app.h_maestro_apartamentos.service.Empresa"
    ) as Emp:
        chain = MagicMock()
        chain.filter_by.return_value = chain
        chain.first.return_value = empresa
        Emp.query = chain
        result = srv._get_xlsx_col_override("emp-1")
    assert result == {"col_id_externo": 1, "col_nombre": 2}


# ── _flatten ──────────────────────────────────────────────────────────────


def test_flatten_messages_list():
    assert srv._flatten({"campo": ["err1"]}) == ["campo: err1"]


def test_flatten_messages_anidado():
    assert srv._flatten({"x": {"y": ["err"]}}) == ["x: err"]
