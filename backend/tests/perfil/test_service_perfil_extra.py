"""Tests adicionales del servicio de perfil (get_perfil, integraciones, configs)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.perfil import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    with app.app_context():
        yield app


def _usuario_mock():
    u = MagicMock()
    u.email = "u@test.com"
    u.rol = "operativo"
    u.empresa_id = "emp-1"
    u.password_changed_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    return u


# ── get_perfil ────────────────────────────────────────────────────────────


def test_get_perfil_usuario_no_existe(app_ctx):
    with patch(
        "app.perfil.service.repo.get_usuario_by_id",
        return_value=None,
    ):
        data = srv.get_perfil("u-1")
    assert data is None


def test_get_perfil_ok(app_ctx):
    with patch(
        "app.perfil.service.repo.get_usuario_by_id",
        return_value=_usuario_mock(),
    ):
        data = srv.get_perfil("u-1")
    assert data["email"] == "u@test.com"
    assert data["empresa_id"] == "emp-1"
    assert "2026-05-01" in data["password_changed_at"]


def test_get_perfil_password_changed_at_none(app_ctx):
    u = _usuario_mock()
    u.password_changed_at = None
    with patch(
        "app.perfil.service.repo.get_usuario_by_id",
        return_value=u,
    ):
        data = srv.get_perfil("u-1")
    assert data["password_changed_at"] is None


# ── actualizar_pms ────────────────────────────────────────────────────────


def test_actualizar_pms_validacion_falla(app_ctx):
    errors = srv.actualizar_pms("emp-1", {})
    assert errors


def test_actualizar_pms_ok(app_ctx):
    with patch(
        "app.perfil.service.encrypt",
        return_value=b"cipher",
    ), patch(
        "app.perfil.service.repo.upsert_pms"
    ) as upsert:
        errors = srv.actualizar_pms(
            "emp-1",
            {"proveedor": "smoobu", "api_key": "x" * 20},
        )
    assert errors == []
    upsert.assert_called_once()


# ── actualizar_ia ─────────────────────────────────────────────────────────


def test_actualizar_ia_validacion_falla(app_ctx):
    errors = srv.actualizar_ia("emp-1", {})
    assert errors


def test_actualizar_ia_fernet_no_configurado(app_ctx):
    with patch(
        "app.perfil.service.encrypt",
        side_effect=RuntimeError("no fernet"),
    ):
        errors = srv.actualizar_ia(
            "emp-1",
            {"proveedor": "openai", "modelo": "gpt-4", "api_key": "k" * 20},
        )
    assert errors
    assert "FERNET" in errors[0]


def test_actualizar_ia_ok_sin_api_key(app_ctx):
    with patch(
        "app.perfil.service.repo.upsert_ia"
    ) as upsert:
        errors = srv.actualizar_ia(
            "emp-1",
            {"proveedor": "openai", "modelo": "gpt-4"},
        )
    assert errors == []
    upsert.assert_called_once()


def test_actualizar_ia_ok_con_api_key(app_ctx):
    with patch(
        "app.perfil.service.encrypt",
        return_value=b"cipher",
    ), patch(
        "app.perfil.service.repo.upsert_ia"
    ):
        errors = srv.actualizar_ia(
            "emp-1",
            {"proveedor": "openai", "modelo": "gpt-4", "api_key": "k" * 20},
        )
    assert errors == []


# ── eliminar pms/ia ────────────────────────────────────────────────────────


def test_eliminar_pms_pasa_a_repo(app_ctx):
    with patch(
        "app.perfil.service.repo.delete_pms"
    ) as delete:
        srv.eliminar_pms("emp-1")
    delete.assert_called_once_with("emp-1")


def test_eliminar_ia_pasa_a_repo(app_ctx):
    with patch(
        "app.perfil.service.repo.delete_ia"
    ) as delete:
        srv.eliminar_ia("emp-1")
    delete.assert_called_once_with("emp-1")


# ── xlsx_apartamentos_config ──────────────────────────────────────────────


def test_get_xlsx_apartamentos_config(app_ctx):
    with patch(
        "app.perfil.service.repo.get_xlsx_apartamentos_config",
        return_value={"col_nombre": 2},
    ):
        data = srv.get_xlsx_apartamentos_config("emp-1")
    assert data == {"col_nombre": 2}


def test_save_xlsx_apartamentos_config_validacion_falla(app_ctx):
    errors = srv.save_xlsx_apartamentos_config(
        "emp-1", {"col_nombre": "no-es-int"}
    )
    assert errors


def test_save_xlsx_apartamentos_config_ok(app_ctx):
    with patch(
        "app.perfil.service.repo.save_xlsx_apartamentos_config"
    ) as save:
        errors = srv.save_xlsx_apartamentos_config(
            "emp-1",
            {"col_id_externo": 1, "col_nombre": 2},
        )
    assert errors == []
    save.assert_called_once()


# ── notif_tardio_config ───────────────────────────────────────────────────


def test_get_notif_tardio_config(app_ctx):
    with patch(
        "app.perfil.service.repo.get_notif_tardio_config",
        return_value={"hora_corte": "21:00"},
    ):
        data = srv.get_notif_tardio_config("emp-1")
    assert data["hora_corte"] == "21:00"


def test_save_notif_tardio_config_validacion_falla(app_ctx):
    errors = srv.save_notif_tardio_config(
        "emp-1", {"hora_corte": "no-hora"}
    )
    assert errors


def test_save_notif_tardio_config_ok(app_ctx):
    with patch(
        "app.perfil.service.repo.save_notif_tardio_config"
    ) as save:
        errors = srv.save_notif_tardio_config(
            "emp-1",
            {"hora_corte": "21:00"},
        )
    assert errors == []
    save.assert_called_once()


# ── _flatten ──────────────────────────────────────────────────────────────


def test_flatten_simple():
    assert srv._flatten({"campo": ["err"]}) == ["campo: err"]
