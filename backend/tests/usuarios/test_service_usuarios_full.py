"""Tests unitarios completos del servicio de usuarios."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.usuarios import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    with app.app_context():
        yield app


def _usuario_mock(rol="operativo"):
    u = MagicMock()
    u.id = "u-1"
    u.email = "u@test.com"
    u.rol = rol
    u.activo = True
    u.created_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    return u


# ── _to_dict ──────────────────────────────────────────────────────────────


def test_to_dict_serializa_campos():
    u = _usuario_mock()
    d = srv._to_dict(u)
    assert d["email"] == "u@test.com"
    assert d["rol"] == "operativo"
    assert "2026-05-01" in d["created_at"]


def test_to_dict_created_at_none():
    u = _usuario_mock()
    u.created_at = None
    d = srv._to_dict(u)
    assert d["created_at"] is None


# ── _max_usuarios ─────────────────────────────────────────────────────────


def test_max_usuarios_sin_empresa_devuelve_default(app_ctx):
    with patch(
        "app.usuarios.service.db.session"
    ) as session:
        session.get.return_value = None
        n = srv._max_usuarios("emp-1")
    assert n == 4


def test_max_usuarios_configuracion_personalizada(app_ctx):
    empresa = MagicMock()
    empresa.configuracion = {"max_usuarios": 10}
    with patch(
        "app.usuarios.service.db.session"
    ) as session:
        session.get.return_value = empresa
        n = srv._max_usuarios("emp-1")
    assert n == 10


def test_max_usuarios_configuracion_none(app_ctx):
    empresa = MagicMock()
    empresa.configuracion = None
    with patch(
        "app.usuarios.service.db.session"
    ) as session:
        session.get.return_value = empresa
        n = srv._max_usuarios("emp-1")
    assert n == 4


# ── listar_usuarios ───────────────────────────────────────────────────────


def test_listar_usuarios_devuelve_lista_y_max(app_ctx):
    u = _usuario_mock()
    with patch(
        "app.usuarios.service.repository.list_by_empresa",
        return_value=[u, u],
    ), patch(
        "app.usuarios.service._max_usuarios",
        return_value=4,
    ):
        data = srv.listar_usuarios("emp-1")
    assert len(data["usuarios"]) == 2
    assert data["max_usuarios"] == 4


# ── crear_usuario ─────────────────────────────────────────────────────────


def test_crear_usuario_validacion_falla(app_ctx):
    data, errors = srv.crear_usuario("emp-1", {"email": "", "rol": ""})
    assert data is None
    assert errors


def test_crear_usuario_email_invalido(app_ctx):
    with patch(
        "app.usuarios.service.sanitize_email",
        return_value=None,
    ):
        data, errors = srv.crear_usuario(
            "emp-1",
            {"email": "no@valido", "rol": "operativo"},
        )
    assert data is None
    assert "correo" in errors[0].lower()


def test_crear_usuario_limite_alcanzado(app_ctx):
    with patch(
        "app.usuarios.service.sanitize_email",
        return_value="u@test.com",
    ), patch(
        "app.usuarios.service._max_usuarios",
        return_value=4,
    ), patch(
        "app.usuarios.service.repository.count_total",
        return_value=4,
    ):
        data, errors = srv.crear_usuario(
            "emp-1",
            {"email": "u@test.com", "rol": "operativo"},
        )
    assert data is None
    assert "Límite" in errors[0]


def test_crear_usuario_email_ya_usado(app_ctx):
    with patch(
        "app.usuarios.service.sanitize_email",
        return_value="u@test.com",
    ), patch(
        "app.usuarios.service._max_usuarios",
        return_value=4,
    ), patch(
        "app.usuarios.service.repository.count_total",
        return_value=2,
    ), patch(
        "app.usuarios.service.repository.find_by_email",
        return_value=MagicMock(),
    ):
        data, errors = srv.crear_usuario(
            "emp-1",
            {"email": "u@test.com", "rol": "operativo"},
        )
    assert data is None
    assert "uso" in errors[0].lower()


def test_crear_usuario_ok(app_ctx):
    u = _usuario_mock()
    with patch(
        "app.usuarios.service.sanitize_email",
        return_value="u@test.com",
    ), patch(
        "app.usuarios.service._max_usuarios",
        return_value=4,
    ), patch(
        "app.usuarios.service.repository.count_total",
        return_value=0,
    ), patch(
        "app.usuarios.service.repository.find_by_email",
        return_value=None,
    ), patch(
        "app.usuarios.service.hash_password",
        return_value="hashed",
    ), patch(
        "app.usuarios.service.repository.create_usuario",
        return_value=u,
    ), patch(
        "app.usuarios.service.db.session"
    ), patch(
        "app.usuarios.service._notificar_password_temporal"
    ):
        data, errors = srv.crear_usuario(
            "emp-1",
            {"email": "u@test.com", "rol": "operativo"},
        )
    assert errors == []
    assert data["usuario"]["email"] == "u@test.com"
    assert "password_temporal" in data


# ── eliminar_usuario ──────────────────────────────────────────────────────


def test_eliminar_usuario_no_existe(app_ctx):
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=None,
    ):
        errors = srv.eliminar_usuario("emp-1", "x", "caller-1")
    assert "no encontrado" in errors[0].lower()


def test_eliminar_usuario_propia_cuenta(app_ctx):
    u = _usuario_mock()
    u.id = "caller-1"
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ):
        errors = srv.eliminar_usuario("emp-1", "caller-1", "caller-1")
    assert "propia" in errors[0].lower()


def test_eliminar_usuario_unico_admin(app_ctx):
    u = _usuario_mock(rol="admin")
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ), patch(
        "app.usuarios.service.repository.count_admins",
        return_value=1,
    ):
        errors = srv.eliminar_usuario("emp-1", "u-1", "caller-X")
    assert "único administrador" in errors[0].lower()


def test_eliminar_usuario_ok(app_ctx):
    u = _usuario_mock(rol="operativo")
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ), patch(
        "app.usuarios.service.repository.delete_usuario"
    ), patch(
        "app.usuarios.service.db.session"
    ):
        errors = srv.eliminar_usuario("emp-1", "u-1", "caller-X")
    assert errors == []


# ── editar_rol ────────────────────────────────────────────────────────────


def test_editar_rol_validacion_falla(app_ctx):
    data, errors = srv.editar_rol("emp-1", "u-1", {"rol": "no-existe"})
    assert data is None
    assert errors


def test_editar_rol_usuario_no_existe(app_ctx):
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=None,
    ):
        data, errors = srv.editar_rol("emp-1", "u-1", {"rol": "operativo"})
    assert data is None
    assert "no encontrado" in errors[0].lower()


def test_editar_rol_unico_admin_no_se_quita(app_ctx):
    u = _usuario_mock(rol="admin")
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ), patch(
        "app.usuarios.service.repository.count_admins",
        return_value=1,
    ):
        data, errors = srv.editar_rol("emp-1", "u-1", {"rol": "operativo"})
    assert data is None
    assert "único administrador" in errors[0].lower()


def test_editar_rol_ok(app_ctx):
    u = _usuario_mock(rol="operativo")
    u_updated = _usuario_mock(rol="admin")
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ), patch(
        "app.usuarios.service.repository.update_usuario",
        return_value=u_updated,
    ), patch(
        "app.usuarios.service.db.session"
    ):
        data, errors = srv.editar_rol("emp-1", "u-1", {"rol": "admin"})
    assert errors == []
    assert data["rol"] == "admin"


# ── resetear_password ─────────────────────────────────────────────────────


def test_resetear_password_no_existe(app_ctx):
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=None,
    ):
        data, errors = srv.resetear_password("emp-1", "u-1")
    assert data is None
    assert "no encontrado" in errors[0].lower()


def test_resetear_password_ok(app_ctx):
    u = _usuario_mock()
    with patch(
        "app.usuarios.service.repository.get_by_id",
        return_value=u,
    ), patch(
        "app.usuarios.service.hash_password",
        return_value="hash",
    ), patch(
        "app.usuarios.service.repository.update_usuario"
    ), patch(
        "app.usuarios.service.db.session"
    ), patch(
        "app.usuarios.service._notificar_password_temporal"
    ):
        data, errors = srv.resetear_password("emp-1", "u-1")
    assert errors == []
    assert "password_temporal" in data


# ── _flatten_errors ───────────────────────────────────────────────────────


def test_flatten_errors_simple():
    assert srv._flatten_errors({"email": ["obligatorio"]}) == ["email: obligatorio"]


def test_flatten_errors_anidado():
    assert srv._flatten_errors({"x": {"y": ["e1"]}}) == ["x: e1"]
