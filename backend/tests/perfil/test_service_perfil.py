"""Tests unitarios del servicio de perfil (defaults de integraciones)."""

from unittest.mock import MagicMock, patch

from app.perfil.service import get_integraciones


def test_get_integraciones_sin_ia_devuelve_proveedor_default():
    with patch("app.perfil.service.repo.get_integraciones",
               return_value={"pms": None, "google": None, "ia": None}):
        data = get_integraciones("emp-1")

    assert data["ia"]["configurado"] is False
    assert data["ia"]["proveedor"] == "default"
    assert data["ia"]["modelo"] is None


def test_get_integraciones_con_ia_byok_devuelve_proveedor_real():
    ia = MagicMock(proveedor="openai", modelo="gpt-4o", api_key_cifrada="cifrada")
    with patch("app.perfil.service.repo.get_integraciones",
               return_value={"pms": None, "google": None, "ia": ia}):
        data = get_integraciones("emp-1")

    assert data["ia"]["configurado"] is True
    assert data["ia"]["proveedor"] == "openai"
    assert data["ia"]["modelo"] == "gpt-4o"


def test_get_integraciones_con_ia_default_sin_apikey_no_marca_configurado():
    ia = MagicMock(proveedor="default", modelo=None, api_key_cifrada=None)
    with patch("app.perfil.service.repo.get_integraciones",
               return_value={"pms": None, "google": None, "ia": ia}):
        data = get_integraciones("emp-1")

    assert data["ia"]["configurado"] is False
    assert data["ia"]["proveedor"] == "default"
