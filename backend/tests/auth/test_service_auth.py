"""Tests unitarios del servicio de autenticación."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from flask import Flask

from app.auth import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret-auth"
    app.config["JWT_ACCESS_TOKEN_HOURS"] = 1
    with app.app_context():
        yield app


# ── sanitize_login_payload ────────────────────────────────────────────────


def test_sanitize_login_validacion_falla():
    data, errors = srv.sanitize_login_payload({"email": "", "password": ""})
    assert data == {}
    assert errors


def test_sanitize_login_email_invalido():
    with patch(
        "app.auth.service.sanitize_email",
        return_value=None,
    ):
        data, errors = srv.sanitize_login_payload(
            {"email": "no-email", "password": "ContraseñaValida123!"}
        )
    assert data == {}
    assert "correo" in errors[0].lower()


def test_sanitize_login_ok():
    with patch(
        "app.auth.service.sanitize_email",
        return_value="u@test.com",
    ):
        data, errors = srv.sanitize_login_payload(
            {"email": "  U@TEST.COM  ", "password": "ContraseñaValida123!"}
        )
    assert errors == []
    assert data["email"] == "u@test.com"


# ── authenticate_user ─────────────────────────────────────────────────────


def test_authenticate_user_no_existe(app_ctx):
    with patch(
        "app.auth.service.find_user_by_email",
        return_value=None,
    ):
        token, errors, must_change = srv.authenticate_user(
            {"email": "u@test.com", "password": "pwd"}
        )
    assert token is None
    assert errors == ["Credenciales incorrectas."]
    assert must_change is False


def test_authenticate_user_inactivo(app_ctx):
    with patch(
        "app.auth.service.find_user_by_email",
        return_value={
            "id": "u-1",
            "email": "u@test.com",
            "password_hash": "hash",
            "empresa_id": "emp-1",
            "rol": "operativo",
            "is_active": False,
        },
    ):
        token, errors, _ = srv.authenticate_user(
            {"email": "u@test.com", "password": "pwd"}
        )
    assert token is None
    assert errors == ["Credenciales incorrectas."]


def test_authenticate_user_password_incorrecta(app_ctx):
    with patch(
        "app.auth.service.find_user_by_email",
        return_value={
            "id": "u-1",
            "email": "u@test.com",
            "password_hash": "hash",
            "empresa_id": "emp-1",
            "rol": "operativo",
            "is_active": True,
        },
    ), patch(
        "app.auth.service.verify_password",
        return_value=False,
    ):
        token, errors, _ = srv.authenticate_user(
            {"email": "u@test.com", "password": "mal"}
        )
    assert token is None
    assert errors == ["Credenciales incorrectas."]


def test_authenticate_user_ok_password_reciente(app_ctx):
    user = {
        "id": "u-1",
        "email": "u@test.com",
        "password_hash": "hash",
        "empresa_id": "emp-1",
        "rol": "operativo",
        "is_active": True,
        "password_changed_at": datetime.now(timezone.utc) - timedelta(days=5),
        "es_superadmin": False,
    }
    with patch(
        "app.auth.service.find_user_by_email",
        return_value=user,
    ), patch(
        "app.auth.service.verify_password",
        return_value=True,
    ):
        token, errors, must_change = srv.authenticate_user(
            {"email": "u@test.com", "password": "ok"}
        )
    assert errors == []
    assert token is not None
    assert must_change is False


def test_authenticate_user_password_caducada(app_ctx):
    user = {
        "id": "u-1",
        "email": "u@test.com",
        "password_hash": "hash",
        "empresa_id": "emp-1",
        "rol": "operativo",
        "is_active": True,
        "password_changed_at": datetime.now(timezone.utc) - timedelta(days=60),
        "es_superadmin": False,
    }
    with patch(
        "app.auth.service.find_user_by_email",
        return_value=user,
    ), patch(
        "app.auth.service.verify_password",
        return_value=True,
    ):
        token, _, must_change = srv.authenticate_user(
            {"email": "u@test.com", "password": "ok"}
        )
    assert token is not None
    assert must_change is True


def test_authenticate_user_password_changed_at_none_fuerza_cambio(app_ctx):
    user = {
        "id": "u-1",
        "email": "u@test.com",
        "password_hash": "hash",
        "empresa_id": "emp-1",
        "rol": "operativo",
        "is_active": True,
        "password_changed_at": None,
        "es_superadmin": False,
    }
    with patch(
        "app.auth.service.find_user_by_email",
        return_value=user,
    ), patch(
        "app.auth.service.verify_password",
        return_value=True,
    ):
        _, _, must_change = srv.authenticate_user(
            {"email": "u@test.com", "password": "ok"}
        )
    assert must_change is True


def test_authenticate_user_password_changed_at_anterior_a_2000_fuerza_cambio(app_ctx):
    user = {
        "id": "u-1",
        "email": "u@test.com",
        "password_hash": "hash",
        "empresa_id": "emp-1",
        "rol": "operativo",
        "is_active": True,
        "password_changed_at": datetime(1999, 1, 1, tzinfo=timezone.utc),
        "es_superadmin": False,
    }
    with patch(
        "app.auth.service.find_user_by_email",
        return_value=user,
    ), patch(
        "app.auth.service.verify_password",
        return_value=True,
    ):
        _, _, must_change = srv.authenticate_user(
            {"email": "u@test.com", "password": "ok"}
        )
    assert must_change is True


# ── _flatten_errors ──────────────────────────────────────────────────────


def test_flatten_errors_lista():
    assert srv._flatten_errors({"email": ["obligatorio"]}) == ["email: obligatorio"]


def test_flatten_errors_anidado():
    assert srv._flatten_errors({"x": {"y": ["err"]}}) == ["x: err"]
