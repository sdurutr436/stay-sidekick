"""Tests unitarios para service.export_csv."""

from unittest.mock import MagicMock, patch


def _pms_config_mock():
    cfg = MagicMock()
    cfg.api_key_cifrada = b"cifrada"
    cfg.proveedor = "smoobu"
    cfg.endpoint = None
    return cfg


def test_export_csv_fechas_validas_llama_fetch_con_isoformat():
    from app.h_sincronizador_contactos.service import export_csv

    pms_mock = MagicMock()
    pms_mock.fetch_reservations.return_value = []

    with (
        patch("app.h_sincronizador_contactos.service.apt_repo.get_pms_config", return_value=_pms_config_mock()),
        patch("app.h_sincronizador_contactos.service.decrypt", return_value="api_key"),
        patch("app.h_sincronizador_contactos.service.build_pms_client", return_value=pms_mock),
        patch("app.h_sincronizador_contactos.service.repo.get_preferencias_contactos", return_value={}),
        patch("app.h_sincronizador_contactos.service.build_csv", return_value=b"Name,Phone\n"),
    ):
        csv_bytes, error = export_csv("empresa_1", {"desde": "2026-05-01", "hasta": "2026-05-31"})

    assert error is None
    assert csv_bytes == b"Name,Phone\n"
    pms_mock.fetch_reservations.assert_called_once_with(desde="2026-05-01", hasta="2026-05-31")


def test_export_csv_fecha_invalida_devuelve_error():
    from app.h_sincronizador_contactos.service import export_csv

    csv_bytes, error = export_csv("empresa_1", {"desde": "no-es-fecha"})

    assert csv_bytes is None
    assert error == "Parámetros de fecha inválidos."


def test_export_csv_sin_fechas_pasa_none():
    from app.h_sincronizador_contactos.service import export_csv

    pms_mock = MagicMock()
    pms_mock.fetch_reservations.return_value = []

    with (
        patch("app.h_sincronizador_contactos.service.apt_repo.get_pms_config", return_value=_pms_config_mock()),
        patch("app.h_sincronizador_contactos.service.decrypt", return_value="api_key"),
        patch("app.h_sincronizador_contactos.service.build_pms_client", return_value=pms_mock),
        patch("app.h_sincronizador_contactos.service.repo.get_preferencias_contactos", return_value={}),
        patch("app.h_sincronizador_contactos.service.build_csv", return_value=b"Name,Phone\n"),
    ):
        csv_bytes, error = export_csv("empresa_1", {})

    assert error is None
    pms_mock.fetch_reservations.assert_called_once_with(desde=None, hasta=None)
