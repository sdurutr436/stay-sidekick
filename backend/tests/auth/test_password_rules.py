"""Tests unitarios de las reglas de fortaleza de contraseñas."""

import pytest

from app.auth.password_rules import (
    MAX_LENGTH,
    MIN_LENGTH,
    PASSWORD_REGEX,
    validate_password,
)


# ── Casos válidos ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("pwd", [
    "Abcdef1!",
    "Larga1234#",
    "Mezcla_1A",
    "Pass.word1",
    "Z9z9z9z9?",
    "MaxLargoTest12345.!",   # exactamente 19 caracteres con especial
])
def test_validate_password_acepta_password_valida(pwd):
    assert validate_password(pwd) is None
    assert PASSWORD_REGEX.match(pwd) is not None


# ── Casos inválidos por longitud ───────────────────────────────────────────


def test_validate_password_rechaza_vacio():
    assert validate_password("") == "La contraseña es obligatoria."


def test_validate_password_rechaza_none():
    assert validate_password(None) == "La contraseña es obligatoria."  # type: ignore[arg-type]


def test_validate_password_rechaza_corta():
    err = validate_password("Ab1!a")
    assert err is not None
    assert "al menos" in err.lower()


def test_validate_password_rechaza_demasiado_larga():
    err = validate_password("A" * 30 + "b1!")
    assert err is not None
    assert str(MAX_LENGTH) in err


# ── Casos inválidos por composición ────────────────────────────────────────


def test_validate_password_rechaza_sin_mayuscula():
    assert validate_password("abcdef1!") == "La contraseña debe contener al menos una letra mayúscula."


def test_validate_password_rechaza_sin_minuscula():
    assert validate_password("ABCDEF1!") == "La contraseña debe contener al menos una letra minúscula."


def test_validate_password_rechaza_sin_numero():
    assert validate_password("AbcdefGh!") == "La contraseña debe contener al menos un número."


def test_validate_password_rechaza_sin_especial():
    assert validate_password("Abcdef12") == "La contraseña debe contener al menos un carácter especial."


# ── Consistencia con la regex compartida ───────────────────────────────────


@pytest.mark.parametrize("pwd", ["abc", "ABCDEFGH", "abcdefgh", "12345678", "Abcdef12"])
def test_password_regex_y_validate_acuerdan_para_invalidos(pwd):
    assert validate_password(pwd) is not None
    assert PASSWORD_REGEX.match(pwd) is None


def test_min_y_max_length_son_los_documentados():
    assert MIN_LENGTH == 8
    assert MAX_LENGTH == 20
