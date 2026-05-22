"""Tests unitarios completos del servicio de sincronización de contactos."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import requests
from flask import Flask
from openpyxl import Workbook

from app.h_sincronizador_contactos import service as srv


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-sincro"
    app.config["GOOGLE_CLIENT_ID"] = "client-id"
    app.config["GOOGLE_CLIENT_SECRET"] = "client-secret"
    app.config["GOOGLE_REDIRECT_URI"] = "http://localhost/callback"
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


def _pms_config(api_key=b"cipher", proveedor="smoobu"):
    cfg = MagicMock()
    cfg.api_key_cifrada = api_key
    cfg.proveedor = proveedor
    cfg.endpoint = None
    return cfg


def _google_integration(activo=True, with_at=True):
    integ = MagicMock()
    integ.activo = activo
    integ.access_token_cifrado = b"at-cipher" if with_at else None
    integ.refresh_token_cifrado = b"rt-cipher"
    integ.token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    integ.alcance = "https://googleapis.com/auth/contacts"
    return integ


# ── OAuth URL / state ──────────────────────────────────────────────────────


def test_build_oauth_url_incluye_client_id_y_state(app_ctx):
    url = srv.build_oauth_url("emp-1")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=client-id" in url
    assert "state=" in url


def test_verify_oauth_state_round_trip(app_ctx):
    url = srv.build_oauth_url("emp-X")
    # extraer state del query
    state = url.split("state=")[1].split("&")[0]
    assert srv.verify_oauth_state(state) == "emp-X"


def test_verify_oauth_state_malformado_devuelve_none(app_ctx):
    assert srv.verify_oauth_state("no-es-un-state-firmado") is None


# ── exchange_code_for_tokens ───────────────────────────────────────────────


def test_exchange_code_http_error_devuelve_false(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.requests.post",
        side_effect=requests.RequestException("boom"),
    ):
        ok, err = srv.exchange_code_for_tokens("code", "emp-1")
    assert ok is False
    assert "Google" in err


def test_exchange_code_sin_refresh_token_devuelve_false(app_ctx):
    resp = MagicMock()
    resp.json.return_value = {"access_token": "at"}  # SIN refresh_token
    resp.raise_for_status.return_value = None
    with patch(
        "app.h_sincronizador_contactos.service.requests.post",
        return_value=resp,
    ):
        ok, err = srv.exchange_code_for_tokens("code", "emp-1")
    assert ok is False
    assert "refresh_token" in err


def test_exchange_code_ok_persiste_tokens(app_ctx):
    resp = MagicMock()
    resp.json.return_value = {
        "access_token": "at",
        "refresh_token": "rt",
        "expires_in": 3600,
        "scope": "scope",
    }
    resp.raise_for_status.return_value = None
    with patch(
        "app.h_sincronizador_contactos.service.requests.post",
        return_value=resp,
    ), patch(
        "app.h_sincronizador_contactos.service.encrypt",
        side_effect=lambda x: b"enc-" + x.encode(),
    ), patch(
        "app.h_sincronizador_contactos.service.repo.upsert_google_tokens"
    ) as upsert, patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        ok, err = srv.exchange_code_for_tokens("code", "emp-1")
    assert ok is True
    assert err is None
    upsert.assert_called_once()


# ── get_google_status / disconnect ─────────────────────────────────────────


def test_get_google_status_sin_integracion_devuelve_no_conectado(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=None,
    ):
        data = srv.get_google_status("emp-1")
    assert data == {"conectado": False}


def test_get_google_status_inactiva_devuelve_no_conectado(app_ctx):
    integ = _google_integration(activo=False)
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=integ,
    ):
        data = srv.get_google_status("emp-1")
    assert data == {"conectado": False}


def test_get_google_status_conectada_devuelve_alcance_y_sync(app_ctx):
    integ = _google_integration()
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=integ,
    ), patch(
        "app.h_sincronizador_contactos.service._ultimo_sync",
        return_value="2026-05-22T10:00:00",
    ):
        data = srv.get_google_status("emp-1")
    assert data["conectado"] is True
    assert data["alcance"] == integ.alcance
    assert data["ultimo_sync"] == "2026-05-22T10:00:00"


def test_disconnect_google_sin_integracion_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=None,
    ):
        err = srv.disconnect_google("emp-1")
    assert "conectada" in err.lower()


def test_disconnect_google_ok_borra_y_commitea(app_ctx):
    integ = _google_integration()
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=integ,
    ), patch(
        "app.h_sincronizador_contactos.service.repo.delete_google_integration"
    ) as delete, patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        err = srv.disconnect_google("emp-1")
    assert err is None
    delete.assert_called_once_with(integ)


# ── Preferencias ───────────────────────────────────────────────────────────


def test_get_preferencias_pasa_a_repo(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={"formato_fecha_salida": "YYMMDD"},
    ):
        data = srv.get_preferencias("emp-1")
    assert data["formato_fecha_salida"] == "YYMMDD"


def test_save_preferencias_validacion_falla_devuelve_errores(app_ctx):
    data, errors = srv.save_preferencias("emp-1", {"formato_fecha_salida": "INVALIDO"})
    assert data is None
    assert errors


def test_save_preferencias_ok_devuelve_dict(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.save_preferencias_contactos",
        return_value={"formato_fecha_salida": "YYMMDD"},
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, errors = srv.save_preferencias(
            "emp-1",
            {"formato_fecha_salida": "YYMMDD"},
        )
    assert errors == []
    assert data["formato_fecha_salida"] == "YYMMDD"


# ── sync_contacts ──────────────────────────────────────────────────────────


def test_sync_contacts_sin_google_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=None,
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert data is None
    assert "Google" in err


def test_sync_contacts_sin_pms_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=None,
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert data is None
    assert "PMS" in err


def test_sync_contacts_decrypt_pms_falla_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        return_value=None,
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert data is None
    assert "descifrar" in err.lower()


def test_sync_contacts_pms_lanza_error(app_ctx):
    pms_client = MagicMock()
    pms_client.fetch_reservations.side_effect = requests.RequestException("boom")
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=["api_pms", "rt", "at"],
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ), patch(
        "app.h_sincronizador_contactos.service._log_sync"
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert data is None
    assert "PMS" in err


def test_sync_contacts_ok_flujo_completo(app_ctx):
    from app.normalizador_pms.base import ReservaEstandar

    reserva = ReservaEstandar(
        id_externo="r1",
        nombre_raw="Ana",
        email=None,
        telefono="+34600000001",
        checkin="2026-05-22",
        checkout="2026-05-25",
        nombre_apartamento="A1",
        id_apartamento_externo=None,
        hora_llegada=None,
        tipo="reservation",
    )
    pms_client = MagicMock()
    pms_client.fetch_reservations.return_value = [reserva]

    google_client = MagicMock()
    google_client.upsert_contact.return_value = (None, True)  # nuevo
    google_client.token_refreshed = False

    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=lambda x: "key",
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={"plantilla": "{NOMBRE}", "formato_fecha_salida": "YYMMDD"},
    ), patch(
        "app.h_sincronizador_contactos.service.GooglePeopleClient",
        return_value=google_client,
    ), patch(
        "app.h_sincronizador_contactos.service._log_sync"
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, err = srv.sync_contacts(
            "emp-1",
            {"desde": "2026-05-01", "hasta": "2026-05-31"},
        )
    assert err is None
    assert data["nuevos"] == 1
    assert data["actualizados"] == 0


def test_sync_contacts_con_errores_devuelve_advertencias(app_ctx):
    from app.normalizador_pms.base import ReservaEstandar

    reserva = ReservaEstandar(
        id_externo="r1",
        nombre_raw="Ana",
        email=None,
        telefono="+34600000001",
        checkin="2026-05-22",
        checkout=None,
        nombre_apartamento=None,
        id_apartamento_externo=None,
        hora_llegada=None,
        tipo="reservation",
    )
    pms_client = MagicMock()
    pms_client.fetch_reservations.return_value = [reserva]

    google_client = MagicMock()
    google_client.upsert_contact.side_effect = requests.RequestException("fail")
    google_client.token_refreshed = False

    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=lambda x: "key",
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service.GooglePeopleClient",
        return_value=google_client,
    ), patch(
        "app.h_sincronizador_contactos.service._log_sync"
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert err is None
    assert "advertencias" in data


def test_sync_contacts_actualiza_access_token_si_refrescado(app_ctx):
    from app.normalizador_pms.base import ReservaEstandar

    pms_client = MagicMock()
    pms_client.fetch_reservations.return_value = []

    new_expiry = datetime.now(timezone.utc) + timedelta(hours=2)
    google_client = MagicMock()
    google_client.token_refreshed = True
    google_client.current_access_token = "nuevo-at"
    google_client.current_token_expiry = new_expiry

    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=lambda x: "key",
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service.GooglePeopleClient",
        return_value=google_client,
    ), patch(
        "app.h_sincronizador_contactos.service.encrypt",
        return_value=b"enc",
    ), patch(
        "app.h_sincronizador_contactos.service.repo.update_access_token"
    ) as update_at, patch(
        "app.h_sincronizador_contactos.service._log_sync"
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, err = srv.sync_contacts("emp-1", {})
    assert err is None
    update_at.assert_called_once()


# ── export_csv ─────────────────────────────────────────────────────────────


def test_export_csv_validacion_falla(app_ctx):
    data, err = srv.export_csv("emp-1", {"desde": "no-fecha"})
    assert data is None
    assert "fecha" in err.lower()


def test_export_csv_sin_pms_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=None,
    ):
        data, err = srv.export_csv("emp-1", {})
    assert data is None
    assert "PMS" in err


def test_export_csv_decrypt_falla(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        return_value=None,
    ):
        data, err = srv.export_csv("emp-1", {})
    assert data is None
    assert "descifrar" in err.lower()


def test_export_csv_pms_error(app_ctx):
    pms_client = MagicMock()
    pms_client.fetch_reservations.side_effect = requests.RequestException("boom")
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ):
        data, err = srv.export_csv("emp-1", {})
    assert data is None
    assert "PMS" in err


def test_export_csv_ok_devuelve_bytes(app_ctx):
    pms_client = MagicMock()
    pms_client.fetch_reservations.return_value = []
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_pms_config",
        return_value=_pms_config(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        return_value="key",
    ), patch(
        "app.h_sincronizador_contactos.service.build_pms_client",
        return_value=pms_client,
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service.build_csv",
        return_value=b"csv-bytes",
    ):
        data, err = srv.export_csv("emp-1", {})
    assert err is None
    assert data == b"csv-bytes"


# ── sync_from_xlsx ─────────────────────────────────────────────────────────


def test_sync_from_xlsx_sin_google_devuelve_error(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=None,
    ):
        data, err = srv.sync_from_xlsx("emp-1", b"")
    assert data is None
    assert "Google" in err


def test_sync_from_xlsx_decrypt_rt_falla(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        return_value=None,
    ):
        data, err = srv.sync_from_xlsx("emp-1", b"")
    assert data is None
    assert "refresh_token" in err.lower()


def test_sync_from_xlsx_parse_error_devuelve_msg(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=lambda x: "key",
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service._parse_xlsx_contactos",
        return_value=([], ["No se pudo abrir el archivo"]),
    ):
        data, err = srv.sync_from_xlsx("emp-1", b"not-an-xlsx")
    assert data is None
    assert "abrir" in err


def test_sync_from_xlsx_ok_flujo(app_ctx):
    from app.h_sincronizador_contactos.contacto_formatter import ContactoAgrupado
    contacto = ContactoAgrupado(
        nombre="Ana",
        telefono="+34600000001",
        checkin_date=None,
        apartamentos=["A1"],
    )

    google_client = MagicMock()
    google_client.upsert_contact.return_value = (None, True)
    google_client.token_refreshed = False

    with patch(
        "app.h_sincronizador_contactos.service.repo.get_google_integration",
        return_value=_google_integration(),
    ), patch(
        "app.h_sincronizador_contactos.service.decrypt",
        side_effect=lambda x: "key",
    ), patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service._parse_xlsx_contactos",
        return_value=([{"nombre": "Ana", "telefono": "+34600000001",
                        "checkin_date": None, "apartamentos": ["A1"]}], []),
    ), patch(
        "app.h_sincronizador_contactos.service.agrupar_contactos",
        return_value=[contacto],
    ), patch(
        "app.h_sincronizador_contactos.service.GooglePeopleClient",
        return_value=google_client,
    ), patch(
        "app.h_sincronizador_contactos.service._log_sync"
    ), patch(
        "app.h_sincronizador_contactos.service.db.session"
    ):
        data, err = srv.sync_from_xlsx("emp-1", b"xlsx-bytes")
    assert err is None
    assert data["nuevos"] == 1


# ── export_csv_from_xlsx ──────────────────────────────────────────────────


def test_export_csv_from_xlsx_parse_error_devuelve_msg(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service._parse_xlsx_contactos",
        return_value=([], ["xlsx malo"]),
    ):
        data, err = srv.export_csv_from_xlsx("emp-1", b"")
    assert data is None
    assert err == "xlsx malo"


def test_export_csv_from_xlsx_ok(app_ctx):
    with patch(
        "app.h_sincronizador_contactos.service.repo.get_preferencias_contactos",
        return_value={},
    ), patch(
        "app.h_sincronizador_contactos.service._parse_xlsx_contactos",
        return_value=([{"nombre": "Ana", "telefono": "+34600000001",
                        "checkin_date": None, "apartamentos": []}], []),
    ), patch(
        "app.h_sincronizador_contactos.service.agrupar_contactos",
        return_value=[],
    ), patch(
        "app.h_sincronizador_contactos.service.build_csv",
        return_value=b"csv",
    ):
        data, err = srv.export_csv_from_xlsx("emp-1", b"xlsx")
    assert err is None
    assert data == b"csv"


# ── _parse_xlsx_contactos ──────────────────────────────────────────────────


def test_parse_xlsx_contactos_archivo_invalido_devuelve_error(app_ctx):
    rows, errs = srv._parse_xlsx_contactos(b"not-an-xlsx", "emp-1", {})
    assert rows == []
    assert errs and "abrir" in errs[0].lower()


def test_parse_xlsx_contactos_sin_nombre_devuelve_error(app_ctx):
    # XLSX con cabeceras desconocidas
    xlsx = _build_xlsx([
        ("desconocida1", "desconocida2"),
        ("a", "b"),
    ])
    rows, errs = srv._parse_xlsx_contactos(xlsx, "emp-1", {})
    assert rows == []
    assert errs


def test_parse_xlsx_contactos_skip_sin_telefono(app_ctx):
    xlsx = _build_xlsx([
        ("nombre", "telefono", "checkin"),
        ("Sin Tel", None, "2026-05-22"),
        ("Con Tel", "+34600000001", "2026-05-22"),
    ])
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_by_id_pms",
        return_value=None,
    ):
        rows, errs = srv._parse_xlsx_contactos(xlsx, "emp-1", {})
    assert len(rows) == 1
    assert rows[0]["nombre"] == "Con Tel"


def test_parse_xlsx_contactos_extrae_ids_tipologia_y_cruza_apt(app_ctx):
    xlsx = _build_xlsx([
        ("nombre", "telefono", "tipologia"),
        ("Ana", "+34600000001", "{42}"),
    ])
    apt = MagicMock()
    apt.nombre = "Apt-42"
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_by_id_pms",
        return_value=apt,
    ):
        rows, _ = srv._parse_xlsx_contactos(xlsx, "emp-1", {})
    assert rows[0]["apartamentos"] == ["Apt-42"]


def test_parse_xlsx_contactos_tipologia_id_inexistente_no_anade(app_ctx):
    xlsx = _build_xlsx([
        ("nombre", "telefono", "tipologia"),
        ("Ana", "+34600000001", "{999}"),
    ])
    with patch(
        "app.h_sincronizador_contactos.service.apt_repo.get_by_id_pms",
        return_value=None,
    ):
        rows, _ = srv._parse_xlsx_contactos(xlsx, "emp-1", {})
    assert rows[0]["apartamentos"] == []


# ── _reservas_a_contactos ──────────────────────────────────────────────────


def test_reservas_a_contactos_filtra_sin_telefono():
    from app.normalizador_pms.base import ReservaEstandar
    r1 = ReservaEstandar(
        id_externo="1", nombre_raw="A", email=None, telefono="+34600000001",
        checkin="2026-05-22", checkout=None, nombre_apartamento="A1",
        id_apartamento_externo=None, hora_llegada=None,
    )
    r2 = ReservaEstandar(
        id_externo="2", nombre_raw="B", email=None, telefono=None,
        checkin=None, checkout=None, nombre_apartamento=None,
        id_apartamento_externo=None, hora_llegada=None,
    )
    contactos = srv._reservas_a_contactos([r1, r2])
    assert len(contactos) == 1


# ── _flatten ───────────────────────────────────────────────────────────────


def test_flatten_messages_simples():
    errors = srv._flatten({"campo": ["error1", "error2"]})
    assert errors == ["campo: error1", "campo: error2"]


def test_flatten_messages_anidados():
    errors = srv._flatten({"pref": {"sub": ["error"]}})
    assert errors == ["pref: error"]


def test_flatten_ignora_estructuras_desconocidas():
    errors = srv._flatten({"campo": "string-no-list"})
    assert errors == []


# ── _log_sync / _ultimo_sync ──────────────────────────────────────────────


def test_log_sync_invoca_repo(app_ctx):
    with patch(
        "app.h_maestro_apartamentos.repository.create_sync_log"
    ) as create:
        srv._log_sync("emp-1", "exito", 5, "ok")
    create.assert_called_once()
