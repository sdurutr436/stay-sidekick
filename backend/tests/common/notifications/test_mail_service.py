"""Tests del servicio de envío de correo transaccional (mail_service)."""

import smtplib
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.common.notifications import mail_service


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def app_configurado():
    app = Flask(__name__)
    app.config.update(
        MAIL_HOST="smtp.test",
        MAIL_PORT=587,
        MAIL_USER="bot@test.com",
        MAIL_PASSWORD="apppass",
        MAIL_FROM="noreply@test.com",
    )
    return app


@pytest.fixture
def app_sin_credenciales():
    app = Flask(__name__)
    app.config.update(
        MAIL_HOST="smtp.test",
        MAIL_PORT=587,
        MAIL_USER="",
        MAIL_PASSWORD="",
        MAIL_FROM="",
    )
    return app


def _mock_smtp_ctx():
    """Devuelve (patch_obj, smtp_instance_mock) listos para asserts."""
    smtp_instance = MagicMock()
    cm = MagicMock()
    cm.__enter__.return_value = smtp_instance
    cm.__exit__.return_value = False
    p = patch("smtplib.SMTP", return_value=cm)
    return p, smtp_instance


# ── send_via_smtp ─────────────────────────────────────────────────────────


def test_send_via_smtp_devuelve_true_y_envia(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        ok, err = mail_service.send_via_smtp(
            to="dest@test.com",
            subject="Hola",
            body_text="cuerpo",
            body_html="<p>cuerpo</p>",
        )
    assert ok is True
    assert err is None
    smtp_instance.login.assert_called_once_with("bot@test.com", "apppass")
    smtp_instance.send_message.assert_called_once()


def test_send_via_smtp_sin_html_solo_texto(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        ok, err = mail_service.send_via_smtp("dest@test.com", "Hola", "cuerpo")
    assert ok is True
    assert err is None
    smtp_instance.send_message.assert_called_once()


def test_send_via_smtp_sin_credenciales_devuelve_false(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        ok, err = mail_service.send_via_smtp("dest@test.com", "x", "y")
    assert ok is False
    assert "SMTP no configurado" in err


def test_send_via_smtp_sin_destinatario_devuelve_false(app_configurado):
    with app_configurado.app_context():
        ok, err = mail_service.send_via_smtp("", "x", "y")
    assert ok is False
    assert "Destinatario vacío" in err


def test_send_via_smtp_smtp_exception_devuelve_false(app_configurado):
    smtp_instance = MagicMock()
    smtp_instance.send_message.side_effect = smtplib.SMTPException("boom")
    cm = MagicMock()
    cm.__enter__.return_value = smtp_instance
    cm.__exit__.return_value = False
    with app_configurado.app_context(), patch("smtplib.SMTP", return_value=cm):
        ok, err = mail_service.send_via_smtp("dest@test.com", "x", "y")
    assert ok is False
    assert "Error al enviar el email" in err


def test_send_via_smtp_oserror_devuelve_false(app_configurado):
    with app_configurado.app_context(), patch(
        "smtplib.SMTP", side_effect=OSError("network down")
    ):
        ok, err = mail_service.send_via_smtp("dest@test.com", "x", "y")
    assert ok is False
    assert "Error al enviar el email" in err


def test_send_via_smtp_usa_mail_user_si_mail_from_vacio(app_configurado):
    app_configurado.config["MAIL_FROM"] = ""
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        ok, _ = mail_service.send_via_smtp("dest@test.com", "x", "y")
    assert ok is True
    msg = smtp_instance.send_message.call_args[0][0]
    assert "bot@test.com" in msg["From"]


# ── send_form_request (caso 1) ────────────────────────────────────────────


def test_send_form_request_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_form_request({"company_name": "X"}) is False


def test_send_form_request_envia_correctamente(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    payload = {
        "company_name": "ACME",
        "company_email": "info@acme.com",
        "phone": "+34911111111",
        "is_member": True,
        "message": "Quiero info",
    }
    with app_configurado.app_context(), p:
        assert mail_service.send_form_request(payload) is True
    msg = smtp_instance.send_message.call_args[0][0]
    assert msg["To"] == "noreply@test.com"
    assert "ACME" in msg["Subject"]


def test_send_form_request_sin_mensaje_usa_placeholder(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        assert mail_service.send_form_request({"company_name": "Z", "is_member": False}) is True
    msg = smtp_instance.send_message.call_args[0][0]
    cuerpo = msg.get_body(preferencelist=("plain",)).get_content()
    assert "(sin mensaje)" in cuerpo


def test_send_form_request_falla_si_smtp_lanza(app_configurado):
    smtp_instance = MagicMock()
    smtp_instance.send_message.side_effect = smtplib.SMTPException("boom")
    cm = MagicMock()
    cm.__enter__.return_value = smtp_instance
    cm.__exit__.return_value = False
    with app_configurado.app_context(), patch("smtplib.SMTP", return_value=cm):
        assert mail_service.send_form_request({"company_name": "X"}) is False


# ── send_contact (caso 2) ─────────────────────────────────────────────────


def test_send_contact_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_contact({"nombre": "Ana"}) is False


def test_send_contact_envia_correctamente(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    payload = {
        "nombre": "Ana",
        "email": "ana@test.com",
        "empresa": "ACME",
        "mensaje": "Hola, tengo una duda",
    }
    with app_configurado.app_context(), p:
        assert mail_service.send_contact(payload) is True
    msg = smtp_instance.send_message.call_args[0][0]
    assert msg["To"] == "noreply@test.com"
    assert "Ana" in msg["Subject"]


def test_send_contact_sin_empresa_y_sin_mensaje(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        assert mail_service.send_contact({"nombre": "Ana", "email": "a@a.com"}) is True
    msg = smtp_instance.send_message.call_args[0][0]
    cuerpo = msg.get_body(preferencelist=("plain",)).get_content()
    assert "(sin empresa)" in cuerpo
    assert "(sin mensaje)" in cuerpo


# ── send_welcome_company (caso 3) ─────────────────────────────────────────


def test_send_welcome_company_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_welcome_company("nuevo@empresa.com", "Nueva") is False


def test_send_welcome_company_envia_a_la_empresa(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        assert mail_service.send_welcome_company("nuevo@empresa.com", "Nueva") is True
    msg = smtp_instance.send_message.call_args[0][0]
    assert msg["To"] == "nuevo@empresa.com"
    assert "Nueva" in msg["Subject"]


# ── send_temp_password (caso 4) ───────────────────────────────────────────


def test_send_temp_password_no_configurado(app_sin_credenciales):
    with app_sin_credenciales.app_context():
        assert mail_service.send_temp_password("user@test.com", "PWD123") is False


def test_send_temp_password_envia_y_contiene_pwd(app_configurado):
    p, smtp_instance = _mock_smtp_ctx()
    with app_configurado.app_context(), p:
        assert mail_service.send_temp_password("user@test.com", "PWD-XY9") is True
    msg = smtp_instance.send_message.call_args[0][0]
    assert msg["To"] == "user@test.com"
    cuerpo = msg.get_body(preferencelist=("plain",)).get_content()
    assert "PWD-XY9" in cuerpo


def test_send_temp_password_falla_si_smtp_lanza(app_configurado):
    smtp_instance = MagicMock()
    smtp_instance.send_message.side_effect = smtplib.SMTPException("boom")
    cm = MagicMock()
    cm.__enter__.return_value = smtp_instance
    cm.__exit__.return_value = False
    with app_configurado.app_context(), patch("smtplib.SMTP", return_value=cm):
        assert mail_service.send_temp_password("user@test.com", "X") is False
