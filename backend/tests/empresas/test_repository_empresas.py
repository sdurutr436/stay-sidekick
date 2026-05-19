"""Tests unitarios del repositorio de empresas."""

from unittest.mock import MagicMock, patch

from app.empresas.repository import crear_empresa, eliminar_empresa
from app.perfil.model import IA_DEFAULT


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


def test_crear_empresa_inserta_configuracion_ia_default():
    with patch("app.empresas.repository.Empresa") as MockEmpresa, \
         patch("app.empresas.repository.ConfiguracionIA") as MockConfigIA, \
         patch("app.empresas.repository.db") as mock_db:
        empresa_instancia = MagicMock(id="emp-uuid-1")
        MockEmpresa.return_value = empresa_instancia

        crear_empresa("Acme", "acme@test.com")

        agregadas = [c.args[0] for c in mock_db.session.add.call_args_list]
        assert empresa_instancia in agregadas
        MockConfigIA.assert_called_once_with(
            empresa_id="emp-uuid-1",
            proveedor=IA_DEFAULT,
            api_key_cifrada=None,
            activo=True,
        )
        mock_db.session.flush.assert_called_once()
        mock_db.session.commit.assert_called_once()
