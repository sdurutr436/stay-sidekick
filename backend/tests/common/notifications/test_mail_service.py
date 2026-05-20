"""Tests del servicio de envío de correo transaccional (mail_service)."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask

from app.common.notifications import mail_service


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def app_configurado():
    app = Flask(__name__)
    app.config.update(
        MAIL_GUN_API_KEY="key-test",
        MAIL_GUN_DOMAIN="mg.test.com",
        MAIL_GUN_API_URL="https://api.eu.mailgun.net",
        MAIL_FROM="noreply@test.com",
    )
    return app


@pytest.fixture
def app_sin_credenciales():
    app = Flask(__name__)
    app.config.update(
        MAIL_GUN_API_KEY="",
        MAIL_GUN_DOMAIN="",
        MAIL_GUN_API_URL="",
        MAIL_FROM="",
    )
    return app


def _mock_response(ok: bool = True, status: int = 200, text: str = "{}"):
    resp = MagicMock()
    resp.ok = ok
    resp.status_code = status
    resp.text = text
    return resp


# ── send_mail ─────────────────────────────────────────────────────────────


def test_send_mail_devuelve_true_y_envia(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        ok, err = mail_service.send_mail(
            to="dest@test.com",
            subject="Hola",
            body_text="cuerpo",
            body_html="<p>cuerpo</p>",
        )
    assert ok is True
    assert err is None
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.eu.mailgun.net/v3/mg.test.com/messages"
    assert kwargs["auth"] == ("api", "key-test")
    data = kwargs["data"]
    assert data["to"] == "dest@test.com"
    assert data["subject"] == "Hola"
    assert data["text"] == "cuerpo"
    assert data["html"] == "<p>cuerpo</p>"
    assert "noreply@test.com" in data["from"]


def test_send_mail_sin_html_solo_texto(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        ok, err = mail_service.send_mail("dest@test.com", "Hola", "cuerpo")
    assert ok is True
    assert err is None
    data = mock_post.call_args.kwargs["data"]
    assert "html" not in data


def test_send_mail_sin_credenciales_devuelve_false(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        ok, err = mail_service.send_mail("dest@test.com", "x", "y")
    assert ok is False
    assert "Mailgun no configurado" in err


def test_send_mail_sin_destinatario_devuelve_false(app_configurado):
    with app_configurado.app_context():
        ok, err = mail_service.send_mail("", "x", "y")
    assert ok is False
    assert "Destinatario vacío" in err


def test_send_mail_error_http_devuelve_false(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(ok=False, status=401, text="unauthorized"),
    ):
        ok, err = mail_service.send_mail("dest@test.com", "x", "y")
    assert ok is False
    assert "HTTP 401" in err


def test_send_mail_request_exception_devuelve_false(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        side_effect=requests.ConnectionError("network down"),
    ):
        ok, err = mail_service.send_mail("dest@test.com", "x", "y")
    assert ok is False
    assert "Error al enviar el email" in err


def test_send_mail_deriva_from_del_dominio_si_mail_from_vacio(app_configurado):
    app_configurado.config["MAIL_FROM"] = ""
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        ok, _ = mail_service.send_mail("dest@test.com", "x", "y")
    assert ok is True
    data = mock_post.call_args.kwargs["data"]
    assert "noreply@mg.test.com" in data["from"]


def test_send_mail_usa_api_url_por_defecto_si_vacia(app_configurado):
    app_configurado.config["MAIL_GUN_API_URL"] = ""
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        ok, _ = mail_service.send_mail("dest@test.com", "x", "y")
    assert ok is True
    assert mock_post.call_args.args[0].startswith("https://api.eu.mailgun.net/")


# ── send_form_request (caso 1) ────────────────────────────────────────────


def test_send_form_request_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_form_request({"company_name": "X"}) is False


def test_send_form_request_envia_correctamente(app_configurado):
    payload = {
        "company_name": "ACME",
        "company_email": "info@acme.com",
        "phone": "+34911111111",
        "is_member": True,
        "message": "Quiero info",
    }
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert mail_service.send_form_request(payload) is True
    data = mock_post.call_args.kwargs["data"]
    assert data["to"] == "noreply@test.com"
    assert "ACME" in data["subject"]
    assert "Quiero info" in data["text"]


def test_send_form_request_sin_mensaje_usa_placeholder(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert (
            mail_service.send_form_request({"company_name": "Z", "is_member": False})
            is True
        )
    data = mock_post.call_args.kwargs["data"]
    assert "(sin mensaje)" in data["text"]


def test_send_form_request_falla_si_http_lanza(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        side_effect=requests.ConnectionError("boom"),
    ):
        assert mail_service.send_form_request({"company_name": "X"}) is False


# ── send_contact (caso 2) ─────────────────────────────────────────────────


def test_send_contact_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_contact({"nombre": "Ana"}) is False


def test_send_contact_envia_correctamente(app_configurado):
    payload = {
        "nombre": "Ana",
        "email": "ana@test.com",
        "empresa": "ACME",
        "mensaje": "Hola, tengo una duda",
    }
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert mail_service.send_contact(payload) is True
    data = mock_post.call_args.kwargs["data"]
    assert data["to"] == "noreply@test.com"
    assert "Ana" in data["subject"]
    assert "Hola, tengo una duda" in data["text"]


def test_send_contact_sin_empresa_y_sin_mensaje(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert (
            mail_service.send_contact({"nombre": "Ana", "email": "a@a.com"}) is True
        )
    data = mock_post.call_args.kwargs["data"]
    assert "(sin empresa)" in data["text"]
    assert "(sin mensaje)" in data["text"]


# ── send_welcome_company (caso 3) ─────────────────────────────────────────


def test_send_welcome_company_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert (
            mail_service.send_welcome_company("nuevo@empresa.com", "Nueva") is False
        )


def test_send_welcome_company_envia_a_la_empresa(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert (
            mail_service.send_welcome_company("nuevo@empresa.com", "Nueva") is True
        )
    data = mock_post.call_args.kwargs["data"]
    assert data["to"] == "nuevo@empresa.com"
    assert "Nueva" in data["subject"]


def test_send_welcome_company_incluye_resumen(app_configurado):
    summary = [
        ("Nombre", "ACME"),
        ("Email registrado", "info@acme.com"),
        ("Fecha de creación", "20/05/2026 10:30 UTC"),
    ]
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert (
            mail_service.send_welcome_company(
                "nuevo@empresa.com", "ACME", summary=summary
            )
            is True
        )
    data = mock_post.call_args.kwargs["data"]
    assert "Resumen de tu cuenta" in data["text"]
    assert "Nombre: ACME" in data["text"]
    assert "info@acme.com" in data["text"]
    assert "20/05/2026 10:30 UTC" in data["text"]
    assert "Resumen de tu cuenta" in data["html"]
    assert "info@acme.com" in data["html"]


# ── send_temp_password (caso 4) ───────────────────────────────────────────


def test_send_temp_password_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_temp_password("user@test.com", "PWD123") is False


def test_send_temp_password_envia_y_contiene_pwd(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        return_value=_mock_response(),
    ) as mock_post:
        assert mail_service.send_temp_password("user@test.com", "PWD-XY9") is True
    data = mock_post.call_args.kwargs["data"]
    assert data["to"] == "user@test.com"
    assert "PWD-XY9" in data["text"]


def test_send_temp_password_falla_si_http_lanza(app_configurado):
    with app_configurado.app_context(), patch(
        "app.common.notifications.mail_service.requests.post",
        side_effect=requests.ConnectionError("boom"),
    ):
        assert mail_service.send_temp_password("user@test.com", "X") is False
