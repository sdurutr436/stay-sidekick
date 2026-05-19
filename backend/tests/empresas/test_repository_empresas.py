"""Tests unitarios del repositorio de empresas (función eliminar_empresa)."""

from unittest.mock import MagicMock, patch

from app.empresas.repository import eliminar_empresa


def test_eliminar_empresa_existente_borra_y_commit():
    empresa_fake = MagicMock()
    with patch("app.empresas.repository.Empresa") as MockEmpresa, \
         patch("app.empresas.repository.db") as mock_db:
        MockEmpresa.query.get.return_value = empresa_fake
        resultado = eliminar_empresa("empresa-uuid-1")

    assert resultado is True
    MockEmpresa.query.get.assert_called_once_with("empresa-uuid-1")
    mock_db.session.delete.assert_called_once_with(empresa_fake)
    mock_db.session.commit.assert_called_once()


def test_eliminar_empresa_inexistente_devuelve_false_sin_tocar_session():
    with patch("app.empresas.repository.Empresa") as MockEmpresa, \
         patch("app.empresas.repository.db") as mock_db:
        MockEmpresa.query.get.return_value = None
        resultado = eliminar_empresa("empresa-no-existe")

    assert resultado is False
    mock_db.session.delete.assert_not_called()
    mock_db.session.commit.assert_not_called()
