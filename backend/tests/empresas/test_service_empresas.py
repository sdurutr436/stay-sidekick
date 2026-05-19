"""Tests unitarios del servicio de empresas (borrado en cascada)."""

import logging
from unittest.mock import patch

from app.empresas.service import borrar_empresa_completa


def test_borrar_empresa_completa_existente_devuelve_true(caplog):
    with patch("app.empresas.service.repository.eliminar_empresa", return_value=True) as mock:
        with caplog.at_level(logging.INFO, logger="app.empresas.service"):
            ok = borrar_empresa_completa("empresa-uuid-1")
    assert ok is True
    mock.assert_called_once_with("empresa-uuid-1")
    assert any("eliminada" in msg.lower() for msg in caplog.messages)


def test_borrar_empresa_completa_inexistente_devuelve_false(caplog):
    with patch("app.empresas.service.repository.eliminar_empresa", return_value=False):
        with caplog.at_level(logging.WARNING, logger="app.empresas.service"):
            ok = borrar_empresa_completa("empresa-fantasma")
    assert ok is False
    assert any("inexistente" in msg.lower() for msg in caplog.messages)
