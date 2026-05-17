"""Tests del servicio de procesamiento del formulario de contacto."""

from unittest.mock import patch

import pytest
from flask import Flask

from app.contact import service as contact_service


@pytest.fixture
def app_ctx():
    return Flask(__name__)


_PAYLOAD_OK = {
    "nombre": "Ana",
    "email": "ana@test.com",
    "empresa": "ACME",
    "mensaje": "Tengo una pregunta importante",
    "turnstile_token": "tok",
}


def test_process_contacto_validacion_falla(app_ctx):
    with app_ctx.test_request_context("/"):
        clean, errors = contact_service.process_contacto({"nombre": ""})
    assert clean == {}
    assert errors


def test_process_contacto_turnstile_falla(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.contact.service.verify_turnstile", return_value=False):
        clean, errors = contact_service.process_contacto(_PAYLOAD_OK)
    assert clean == {}
    assert "captcha" in errors[0].lower()


def test_process_contacto_exitoso_dispara_notificaciones(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.contact.service.verify_turnstile", return_value=True), \
         patch("app.contact.service.send_contact", return_value=True) as mail_mock, \
         patch("app.contact.service.send_discord_contact_notification", return_value=True):
        clean, errors = contact_service.process_contacto(_PAYLOAD_OK)
    assert errors == []
    assert clean["email"] == "ana@test.com"
    mail_mock.assert_called_once()


def test_dispatch_notifications_excepciones_silenciosas(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.contact.service.send_contact", side_effect=RuntimeError("smtp")), \
         patch("app.contact.service.send_discord_contact_notification", side_effect=RuntimeError("disc")):
        contact_service._dispatch_notifications({"email": "x@x.com"})  # no debe lanzar


def test_dispatch_notifications_falla_loguea_warning(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.contact.service.send_contact", return_value=False), \
         patch("app.contact.service.send_discord_contact_notification", return_value=False):
        contact_service._dispatch_notifications({"email": "x@x.com"})  # no debe lanzar
