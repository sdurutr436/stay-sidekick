"""Tests del servicio de procesamiento del formulario de solicitud."""

from unittest.mock import patch

import pytest
from flask import Flask
from marshmallow import ValidationError

from app.solicitud import service as solicitud_service


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    return app


_PAYLOAD_OK = {
    "company_name": "ACME",
    "company_email": "info@acme.com",
    "country_code": "ES",
    "phone": "911111111",
    "is_member": True,
    "message": "Quiero info",
    "turnstile_token": "tok",
    "privacy_accepted": True,
}


def test_process_solicitud_validacion_falla(app_ctx):
    with app_ctx.test_request_context("/"):
        clean, errors = solicitud_service.process_solicitud({"company_name": ""})
    assert clean == {}
    assert errors  # algún error de validación


def test_process_solicitud_turnstile_falla(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.solicitud.service.verify_turnstile", return_value=False):
        clean, errors = solicitud_service.process_solicitud(_PAYLOAD_OK)
    assert clean == {}
    assert "captcha" in errors[0].lower()


def test_process_solicitud_exitoso_dispara_notificaciones(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.solicitud.service.verify_turnstile", return_value=True), \
         patch("app.solicitud.service.send_form_request", return_value=True) as mail_mock, \
         patch("app.solicitud.service.send_discord_notification", return_value=True):
        clean, errors = solicitud_service.process_solicitud(_PAYLOAD_OK)
    assert errors == []
    assert clean["company_email"] == "info@acme.com"
    mail_mock.assert_called_once()


def test_flatten_errors_con_dict_anidado():
    msgs = {
        "phone": ["bad"],
        "wrapper": {"sub": ["nested error"]},
    }
    out = solicitud_service._flatten_errors(msgs)
    assert "phone: bad" in out
    assert "wrapper: nested error" in out


def test_flatten_errors_validation_error(app_ctx):
    try:
        raise ValidationError({"email": ["inválido"]})
    except ValidationError as exc:
        out = solicitud_service._flatten_errors(exc.messages)
    assert out == ["email: inválido"]


def test_dispatch_notifications_excepciones_silenciosas(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.solicitud.service.send_form_request", side_effect=RuntimeError("smtp")), \
         patch("app.solicitud.service.send_discord_notification", side_effect=RuntimeError("disc")):
        solicitud_service._dispatch_notifications({"company_name": "X"})  # no debe lanzar


def test_dispatch_notifications_falla_loguea_warning(app_ctx):
    with app_ctx.test_request_context("/"), \
         patch("app.solicitud.service.send_form_request", return_value=False), \
         patch("app.solicitud.service.send_discord_notification", return_value=False):
        solicitud_service._dispatch_notifications({"company_name": "X"})  # no debe lanzar
