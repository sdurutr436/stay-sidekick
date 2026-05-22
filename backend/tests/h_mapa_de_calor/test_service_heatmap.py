"""Tests unitarios completos del servicio del mapa de calor."""

from datetime import date
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask
from openpyxl import Workbook

from app.h_mapa_de_calor import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    with app.app_context():
        yield app


def _build_xlsx(rows: list[tuple]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _pms_config(api_key=b"cipher"):
    cfg = MagicMock()
    cfg.api_key_cifrada = api_key
    cfg.proveedor = "smoobu"
    cfg.endpoint = None
    return cfg


# ── Umbrales ───────────────────────────────────────────────────────────────


def test_get_umbrales_pasa_a_repo(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.get_umbrales",
        return_value={"nivel1": 1, "nivel2": 3, "nivel3": 5},
    ):
        data = srv.get_umbrales("emp-1")
    assert data["nivel1"] == 1


def test_save_umbrales_validacion_falla(app_ctx):
    data, errors = srv.save_umbrales("emp-1", {"nivel1": 5, "nivel2": 3, "nivel3": 1})
    assert data is None
    assert errors


def test_save_umbrales_ok(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.save_umbrales",
        return_value={"nivel1": 1, "nivel2": 3, "nivel3": 5},
    ), patch(
        "app.h_mapa_de_calor.service.db.session"
    ):
        data, errors = srv.save_umbrales(
            "emp-1", {"nivel1": 1, "nivel2": 3, "nivel3": 5}
        )
    assert errors == []
    assert data["nivel3"] == 5


# ── Config XLSX ────────────────────────────────────────────────────────────


def test_get_config_xlsx_pasa_a_repo(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "B"},
    ):
        data = srv.get_config_xlsx("emp-1")
    assert data["col_fecha_checkin"] == "B"


def test_save_config_xlsx_validacion_falla(app_ctx):
    data, errors = srv.save_config_xlsx("emp-1", {"col_fecha_checkin": ""})
    assert data is None
    assert errors


def test_save_config_xlsx_ok(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.save_config_xlsx",
        return_value={"col_fecha_checkin": "B", "col_fecha_checkout": "C"},
    ), patch(
        "app.h_mapa_de_calor.service.db.session"
    ):
        data, errors = srv.save_config_xlsx(
            "emp-1", {"col_fecha_checkin": "B", "col_fecha_checkout": "C"}
        )
    assert errors == []
    assert data["col_fecha_checkin"] == "B"


# ── generar_desde_pms ──────────────────────────────────────────────────────


def test_generar_desde_pms_sin_pms_devuelve_error(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.apt_repo.get_pms_config",
        return_value=None,
    ):
        data, err = srv.generar_desde_pms(
            "emp-1", date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "PMS" in err


def test_generar_desde_pms_decrypt_falla(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_mapa_de_calor.service.decrypt",
        return_value=None,
    ):
        data, err = srv.generar_desde_pms(
            "emp-1", date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "descifrar" in err.lower()


def test_generar_desde_pms_error_externo(app_ctx):
    client_mock = MagicMock()
    client_mock.fetch_reservations.side_effect = requests.RequestException("boom")
    with patch(
        "app.h_mapa_de_calor.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_mapa_de_calor.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_mapa_de_calor.service.build_pms_client",
        return_value=client_mock,
    ):
        data, err = srv.generar_desde_pms(
            "emp-1", date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "PMS" in err


def test_generar_desde_pms_ok_devuelve_dias(app_ctx):
    from app.normalizador_pms.base import ReservaEstandar
    r_in = ReservaEstandar(
        id_externo="1", nombre_raw="A", email=None, telefono=None,
        checkin="2026-05-23", checkout=None, nombre_apartamento=None,
        id_apartamento_externo=None, hora_llegada=None, tipo="reservation",
    )
    r_out = ReservaEstandar(
        id_externo="2", nombre_raw="B", email=None, telefono=None,
        checkin=None, checkout="2026-05-25", nombre_apartamento=None,
        id_apartamento_externo=None, hora_llegada=None, tipo="reservation",
    )
    r_cancelled = ReservaEstandar(
        id_externo="3", nombre_raw="cancelado", email=None, telefono=None,
        checkin="2026-05-23", checkout=None, nombre_apartamento=None,
        id_apartamento_externo=None, hora_llegada=None, tipo="cancellation",
    )
    # tipo=None es el caso real de Smoobu para reservas normales — debe contarse.
    r_normal = ReservaEstandar(
        id_externo="4", nombre_raw="normal", email=None, telefono=None,
        checkin=None, checkout="2026-05-25", nombre_apartamento=None,
        id_apartamento_externo=None, hora_llegada=None, tipo=None,
    )
    client_mock = MagicMock()
    client_mock.fetch_reservations.return_value = [r_in, r_cancelled]
    client_mock.fetch_by_departure.return_value = [r_out, r_normal]

    with patch(
        "app.h_mapa_de_calor.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_mapa_de_calor.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_mapa_de_calor.service.build_pms_client",
        return_value=client_mock,
    ), patch(
        "app.h_mapa_de_calor.service.repo.create_sync_log"
    ), patch(
        "app.h_mapa_de_calor.service.db.session"
    ):
        data, err = srv.generar_desde_pms(
            "emp-1", date(2026, 5, 22), date(2026, 5, 28)
        )
    assert err is None
    dia_23 = next(d for d in data if d["fecha"] == "2026-05-23")
    dia_25 = next(d for d in data if d["fecha"] == "2026-05-25")
    # r_in (reservation) cuenta como check-in; r_cancelled queda fuera.
    assert dia_23["checkins"] == 1
    # r_out (reservation) y r_normal (tipo=None) cuentan como check-outs.
    assert dia_25["checkouts"] == 2


# ── generar_desde_xlsx ─────────────────────────────────────────────────────


def test_generar_desde_xlsx_sin_columna_checkin_devuelve_error(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": None},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", b"x", None, date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "check-in" in err.lower()


def test_generar_desde_xlsx_checkouts_sin_columna_devuelve_error(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A", "col_fecha_checkout": None},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", b"x", b"y", date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "check-out" in err.lower()


def test_generar_desde_xlsx_letra_columna_invalida(app_ctx):
    xlsx = _build_xlsx([("fecha",), ("2026-05-23",)])
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "@@@"},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", xlsx, None, date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "letra" in err.lower()


def test_generar_desde_xlsx_archivo_invalido(app_ctx):
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A"},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", b"not-xlsx", None, date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "abrir" in err.lower()


def test_generar_desde_xlsx_solo_cabecera(app_ctx):
    xlsx = _build_xlsx([("fecha",)])
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A"},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", xlsx, None, date(2026, 5, 22), date(2026, 5, 28)
        )
    assert data is None
    assert "filas" in err.lower()


def test_generar_desde_xlsx_ok_solo_checkins(app_ctx):
    xlsx = _build_xlsx([
        ("fecha",),
        ("2026-05-23",),
        ("2026-05-23",),
        ("2026-05-24",),
        ("fecha-mala",),  # descartada (no parseable)
    ])
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A"},
    ), patch(
        "app.h_mapa_de_calor.service.repo.create_sync_log"
    ), patch(
        "app.h_mapa_de_calor.service.db.session"
    ):
        data, warnings, err = srv.generar_desde_xlsx(
            "emp-1", xlsx, None, date(2026, 5, 22), date(2026, 5, 28)
        )
    assert err is None
    dia_23 = next(d for d in data if d["fecha"] == "2026-05-23")
    assert dia_23["checkins"] == 2
    assert warnings  # 1 fila descartada por fecha no parseable


def test_generar_desde_xlsx_con_checkouts(app_ctx):
    xlsx_in = _build_xlsx([("fecha",), ("2026-05-23",)])
    xlsx_out = _build_xlsx([("fecha",), ("2026-05-25",)])
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A", "col_fecha_checkout": "A"},
    ), patch(
        "app.h_mapa_de_calor.service.repo.create_sync_log"
    ), patch(
        "app.h_mapa_de_calor.service.db.session"
    ):
        data, warnings, err = srv.generar_desde_xlsx(
            "emp-1", xlsx_in, xlsx_out,
            date(2026, 5, 22), date(2026, 5, 28),
        )
    assert err is None
    dia_25 = next(d for d in data if d["fecha"] == "2026-05-25")
    assert dia_25["checkouts"] == 1


def test_generar_desde_xlsx_checkouts_invalido(app_ctx):
    xlsx_in = _build_xlsx([("fecha",), ("2026-05-23",)])
    with patch(
        "app.h_mapa_de_calor.service.repo.get_config_xlsx",
        return_value={"col_fecha_checkin": "A", "col_fecha_checkout": "A"},
    ):
        data, ws, err = srv.generar_desde_xlsx(
            "emp-1", xlsx_in, b"not-xlsx",
            date(2026, 5, 22), date(2026, 5, 28),
        )
    assert data is None
    assert "abrir" in err.lower()


# ── _col_letra_a_idx ──────────────────────────────────────────────────────


def test_col_letra_a_idx_simple():
    assert srv._col_letra_a_idx("A") == 0
    assert srv._col_letra_a_idx("B") == 1
    assert srv._col_letra_a_idx("Z") == 25
    assert srv._col_letra_a_idx("AA") == 26


def test_col_letra_a_idx_lowercase_ok():
    assert srv._col_letra_a_idx("aa") == 26


def test_col_letra_a_idx_invalido():
    assert srv._col_letra_a_idx("") is None
    assert srv._col_letra_a_idx("1") is None
    assert srv._col_letra_a_idx("A1") is None


# ── _sanitize_xlsx ────────────────────────────────────────────────────────


def test_sanitize_xlsx_borra_celdas_con_formulas_prefix():
    xlsx = _build_xlsx([
        ("col",),
        ("=SUM(A1)",),
        ("+inyectado",),
        ("@vulnerabilidad",),
        ("-malicioso",),
        ("seguro",),
    ])
    wb = srv._sanitize_xlsx(xlsx)
    ws = wb.active
    values = [row[0].value for row in ws.iter_rows()]
    assert "=SUM(A1)" not in values
    assert "seguro" in values
    wb.close()


# ── _construir_grid ───────────────────────────────────────────────────────


def test_construir_grid_marca_mes_adyacente():
    # 22-may-2026 es viernes → empieza grid en lunes 18
    dias = srv._construir_grid(
        date(2026, 5, 22), date(2026, 5, 22),
        {}, {},
    )
    iso_22 = next(d for d in dias if d["fecha"] == "2026-05-22")
    iso_18 = next(d for d in dias if d["fecha"] == "2026-05-18")
    assert iso_22["mesAdyacente"] is False
    assert iso_18["mesAdyacente"] is True


def test_construir_grid_completa_semanas():
    # 22-may-2026 (viernes) a 22-may-2026 (viernes) → 7 días (lun→dom)
    dias = srv._construir_grid(
        date(2026, 5, 22), date(2026, 5, 22),
        {}, {},
    )
    assert len(dias) == 7


# ── _flatten ───────────────────────────────────────────────────────────────


def test_flatten_lista():
    assert srv._flatten({"x": ["a", "b"]}) == ["x: a", "x: b"]


def test_flatten_string():
    assert srv._flatten({"x": "err"}) == ["x: err"]


def test_flatten_dict_anidado():
    assert srv._flatten({"x": {"y": ["err"]}}) == ["x: err"]
