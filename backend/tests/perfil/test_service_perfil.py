"""Tests unitarios del servicio de perfil (defaults de integraciones)."""

from unittest.mock import MagicMock, patch

from app.perfil.service import cambiar_password, get_integraciones


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


# ── cambiar_password — validación de fortaleza ─────────────────────────────


def test_cambiar_password_rechaza_nueva_debil_antes_de_consultar_bd():
    payload = {"password_actual": "loQueSea1!", "password_nueva": "abc"}
    with patch("app.perfil.service.repo.get_usuario_by_id") as mock_get:
        errors = cambiar_password("user-1", payload)
        mock_get.assert_not_called()
    assert errors and "al menos" in errors[0].lower()


def test_cambiar_password_rechaza_si_supera_maximo():
    payload = {"password_actual": "loQueSea1!", "password_nueva": "A" * 25 + "b1!"}
    errors = cambiar_password("user-1", payload)
    assert errors and "20" in errors[0]


def test_cambiar_password_rechaza_si_confirm_no_coincide():
    payload = {
        "password_actual":  "loQueSea1!",
        "password_nueva":   "Abcdef12!",
        "password_confirm": "Abcdef99!",
    }
    errors = cambiar_password("user-1", payload)
    assert errors == ["Las contraseñas no coinciden."]


def test_cambiar_password_no_valida_fortaleza_de_actual():
    """La contraseña actual nunca se valida en fortaleza, solo en hash."""
    usuario = MagicMock(password_hash="hash-bcrypt")
    payload = {
        "password_actual":  "x",  # contraseña actual débil — debe pasar fortaleza
        "password_nueva":   "Abcdef12!",
        "password_confirm": "Abcdef12!",
    }
    with patch("app.perfil.service.repo.get_usuario_by_id", return_value=usuario), \
         patch("app.perfil.service.verify_password", return_value=False) as mock_verify:
        errors = cambiar_password("user-1", payload)

    mock_verify.assert_called_once()  # llega a la verificación de bcrypt
    assert errors == ["La contraseña actual no es correcta."]


def test_cambiar_password_exitoso_con_password_valida():
    usuario = MagicMock(password_hash="hash-bcrypt")
    payload = {
        "password_actual":  "loQueSea1!",
        "password_nueva":   "Abcdef12!",
        "password_confirm": "Abcdef12!",
    }
    with patch("app.perfil.service.repo.get_usuario_by_id", return_value=usuario), \
         patch("app.perfil.service.verify_password", return_value=True), \
         patch("app.perfil.service.hash_password", return_value="hash-nuevo"), \
         patch("app.perfil.service.repo.update_password") as mock_update:
        errors = cambiar_password("user-1", payload)

    assert errors == []
    mock_update.assert_called_once_with(usuario, "hash-nuevo")
