"""Tests del servicio de usuarios — focalizados en envío de contraseña temporal."""

from unittest.mock import patch

from app.usuarios.service import _notificar_password_temporal, generar_password_temporal


def test_generar_password_temporal_devuelve_string_no_vacio():
    pwd = generar_password_temporal()
    assert isinstance(pwd, str)
    assert len(pwd) >= 8


def test_notificar_password_temporal_envia():
    with patch("app.usuarios.service.send_temp_password", return_value=True) as mock:
        _notificar_password_temporal("u@test.com", "PWD123")
    mock.assert_called_once_with("u@test.com", "PWD123")


def test_notificar_password_temporal_falla_silenciosamente():
    with patch("app.usuarios.service.send_temp_password", return_value=False):
        _notificar_password_temporal("u@test.com", "PWD123")  # no debe lanzar


def test_notificar_password_temporal_excepcion_silenciosa():
    with patch("app.usuarios.service.send_temp_password", side_effect=RuntimeError("smtp")):
        _notificar_password_temporal("u@test.com", "PWD123")  # no debe lanzar
