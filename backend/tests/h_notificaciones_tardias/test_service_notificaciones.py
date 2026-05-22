"""Tests unitarios del servicio de notificaciones de check-in tardío."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from openpyxl import Workbook

from app.h_notificaciones_tardias.service import (
    _norm_id,
    _reserva_a_dict,
    enviar_notificacion,
    get_status,
    parse_checkins_xlsx,
)
from app.normalizador_pms.base import ReservaEstandar


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config["MAIL_GUN_API_KEY"] = ""
    app.config["MAIL_GUN_DOMAIN"] = ""
    with app.app_context():
        yield app


@pytest.fixture
def app_ctx_con_mail():
    app = Flask(__name__)
    app.config["MAIL_GUN_API_KEY"] = "key"
    app.config["MAIL_GUN_DOMAIN"] = "example.com"
    with app.app_context():
        yield app


# ── _norm_id ──────────────────────────────────────────────────────────────


def test_norm_id_strip_y_llaves():
    assert _norm_id("{4}") == "4"
    assert _norm_id("  04  ") == "4"
    assert _norm_id("{APT-12}") == "APT-12"


def test_norm_id_devuelve_string_si_no_es_int():
    assert _norm_id("ABC") == "ABC"


def test_norm_id_acepta_int():
    assert _norm_id(4) == "4"


# ── _reserva_a_dict ───────────────────────────────────────────────────────


def _reserva(**overrides) -> ReservaEstandar:
    base = dict(
        id_externo="r-1",
        nombre_raw="Juan",
        email="j@x.com",
        telefono="600",
        checkin="2026-05-22",
        checkout="2026-05-25",
        nombre_apartamento="A1",
        id_apartamento_externo=None,
        hora_llegada="21:00",
    )
    base.update(overrides)
    return ReservaEstandar(**base)


def test_reserva_a_dict_sin_apartamentos_devuelve_solo_reserva():
    r = _reserva()
    d = _reserva_a_dict(r)
    assert d["nombre"] == "Juan"
    assert d["apartamento"] == "A1"
    assert d["direccion"] is None
    assert d["hora_llegada"] == "21:00"


def test_reserva_a_dict_cruza_apartamento_por_id_externo():
    apt = MagicMock()
    apt.nombre = "Apt Real"
    apt.direccion = "Calle Falsa 123"
    apt.id_externo = "{4}"
    apts = {_norm_id("{4}"): apt}
    r = _reserva(id_apartamento_externo="4", nombre_apartamento="otro")
    d = _reserva_a_dict(r, apts)
    assert d["apartamento"] == "Apt Real"
    assert d["direccion"] == "Calle Falsa 123"


def test_reserva_a_dict_cruza_por_nombre_apartamento_si_no_hay_id_externo():
    apt = MagicMock()
    apt.nombre = "Apt Real"
    apt.direccion = "Dir"
    apts = {"4": apt}
    r = _reserva(id_apartamento_externo=None, nombre_apartamento="4")
    d = _reserva_a_dict(r, apts)
    assert d["apartamento"] == "Apt Real"


# ── get_status ────────────────────────────────────────────────────────────


def test_get_status_sin_pms_ni_mail(app_ctx):
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=None,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={"hora_corte": "20:00"},
    ):
        data = get_status("emp-1")
    assert data["mail_configurado"] is False
    assert data["pms_configurado"] is False
    assert data["pms_error"] is None
    assert data["apartamentos"] == []
    assert data["reservas_pms"] == []
    assert data["hora_corte"] == "20:00"


def test_get_status_con_mail_configurado(app_ctx_con_mail):
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=None,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={"hora_corte": "20:00"},
    ):
        data = get_status("emp-1")
    assert data["mail_configurado"] is True


def test_get_status_con_pms_y_reservas(app_ctx):
    apt = MagicMock()
    apt.id = "a1"
    apt.nombre = "A1"
    apt.ciudad = "Cádiz"
    apt.id_externo = "ext-1"
    apt.direccion = "Calle 1"

    pms_config = MagicMock()
    pms_config.api_key_cifrada = b"cipher"
    pms_config.proveedor = "smoobu"
    pms_config.endpoint = None

    reserva = _reserva(tipo="reservation")
    client_mock = MagicMock()
    client_mock.fetch_reservations.return_value = [reserva]

    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[apt],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=pms_config,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={"hora_corte": "20:00"},
    ), patch(
        "app.h_notificaciones_tardias.service.decrypt",
        return_value="api_key",
    ), patch(
        "app.h_notificaciones_tardias.service.build_pms_client",
        return_value=client_mock,
    ):
        data = get_status("emp-1", fecha="2026-05-22")

    assert data["pms_configurado"] is True
    assert data["pms_error"] is None
    assert len(data["apartamentos"]) == 1
    assert len(data["reservas_pms"]) == 1
    client_mock.fetch_reservations.assert_called_once_with(
        desde="2026-05-22", hasta="2026-05-22"
    )


def test_get_status_pms_lanza_excepcion_devuelve_pms_error(app_ctx):
    pms_config = MagicMock()
    pms_config.api_key_cifrada = b"cipher"
    pms_config.proveedor = "smoobu"
    pms_config.endpoint = None

    client_mock = MagicMock()
    client_mock.fetch_reservations.side_effect = RuntimeError("boom")

    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=pms_config,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={},
    ), patch(
        "app.h_notificaciones_tardias.service.decrypt",
        return_value="api_key",
    ), patch(
        "app.h_notificaciones_tardias.service.build_pms_client",
        return_value=client_mock,
    ):
        data = get_status("emp-1")

    assert data["pms_configurado"] is True
    assert data["pms_error"] == "No se pudieron cargar las reservas del PMS."


def test_get_status_decrypt_devuelve_vacio_no_marca_pms_configurado(app_ctx):
    pms_config = MagicMock()
    pms_config.api_key_cifrada = b"cipher"

    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=pms_config,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={},
    ), patch(
        "app.h_notificaciones_tardias.service.decrypt",
        return_value="",
    ):
        data = get_status("emp-1")

    assert data["pms_configurado"] is False


def test_get_status_fecha_invalida_usa_today(app_ctx):
    pms_config = MagicMock()
    pms_config.api_key_cifrada = b"cipher"
    pms_config.proveedor = "smoobu"
    pms_config.endpoint = None

    client_mock = MagicMock()
    client_mock.fetch_reservations.return_value = []

    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ), patch(
        "app.h_notificaciones_tardias.service.apt_repo.get_pms_config",
        return_value=pms_config,
    ), patch(
        "app.h_notificaciones_tardias.service.perfil_repo.get_notif_tardio_config",
        return_value={},
    ), patch(
        "app.h_notificaciones_tardias.service.decrypt",
        return_value="api_key",
    ), patch(
        "app.h_notificaciones_tardias.service.build_pms_client",
        return_value=client_mock,
    ):
        data = get_status("emp-1", fecha="no-es-fecha")

    # No casca; usa fecha hoy. Solo verificamos que vino llamado con misma fecha desde/hasta.
    assert data["pms_configurado"] is True
    args, kwargs = client_mock.fetch_reservations.call_args
    assert kwargs["desde"] == kwargs["hasta"]


# ── parse_checkins_xlsx ───────────────────────────────────────────────────


def _build_xlsx(rows: list[tuple]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_checkins_xlsx_filtra_solo_tardias():
    xlsx_bytes = _build_xlsx([
        ("nombre", "hora_llegada", "checkin"),
        ("Juan", "21:00", "2026-05-22"),
        ("Ana", "10:00", "2026-05-22"),
        ("Pepe", "20:30", "2026-05-22"),
    ])
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ):
        tardias, errores = parse_checkins_xlsx(
            xlsx_bytes, "emp-1", "20:00", {}
        )
    nombres = [t["nombre"] for t in tardias]
    assert "Juan" in nombres
    assert "Pepe" in nombres
    assert "Ana" not in nombres


def test_parse_checkins_xlsx_aplica_col_overrides():
    # Sin cabeceras reconocidas; usamos col_config con letras explícitas
    xlsx_bytes = _build_xlsx([
        ("col-a", "col-b", "col-c"),
        ("Juan", "2026-05-22", "21:00"),
    ])
    col_config = {
        "col_nombre": "A",
        "col_checkin": "B",
        "col_hora_llegada": "C",
    }
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ):
        tardias, errores = parse_checkins_xlsx(
            xlsx_bytes, "emp-1", "20:00", col_config
        )
    assert len(tardias) == 1
    assert tardias[0]["nombre"] == "Juan"


def test_parse_checkins_xlsx_letra_invalida_se_ignora():
    xlsx_bytes = _build_xlsx([
        ("nombre", "hora_llegada"),
        ("Juan", "21:00"),
    ])
    col_config = {"col_nombre": "@@@"}  # letra inválida → ValueError silencioso
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ):
        tardias, _ = parse_checkins_xlsx(
            xlsx_bytes, "emp-1", "20:00", col_config
        )
    assert len(tardias) == 1


def test_parse_checkins_xlsx_excluye_sin_hora_llegada():
    xlsx_bytes = _build_xlsx([
        ("nombre", "hora_llegada"),
        ("Juan", None),
        ("Ana", "23:00"),
    ])
    with patch(
        "app.h_notificaciones_tardias.service.apt_repo.list_by_empresa",
        return_value=[],
    ):
        tardias, _ = parse_checkins_xlsx(
            xlsx_bytes, "emp-1", "20:00", {}
        )
    assert len(tardias) == 1
    assert tardias[0]["nombre"] == "Ana"


# ── enviar_notificacion ───────────────────────────────────────────────────


def test_enviar_notificacion_ok():
    with patch(
        "app.h_notificaciones_tardias.service.send_mail",
        return_value=(True, None),
    ):
        ok, err = enviar_notificacion("a@b.com", "Asunto", "Mensaje")
    assert ok is True
    assert err is None


def test_enviar_notificacion_error():
    with patch(
        "app.h_notificaciones_tardias.service.send_mail",
        return_value=(False, "smtp"),
    ):
        ok, err = enviar_notificacion("a@b.com", "Asunto", "Mensaje")
    assert ok is False
    assert err == "smtp"
