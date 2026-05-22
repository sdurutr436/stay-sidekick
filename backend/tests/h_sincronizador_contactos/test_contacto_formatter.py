"""Tests unitarios del módulo contacto_formatter."""

from datetime import date

from app.h_sincronizador_contactos.contacto_formatter import (
    ContactoAgrupado,
    agrupar_contactos,
    aplicar_plantilla,
    formatear_fecha_salida,
    parsear_fecha,
    parsear_telefono,
)


# ── parsear_fecha ─────────────────────────────────────────────────────────


def test_parsear_fecha_none_devuelve_none():
    assert parsear_fecha(None) is None


def test_parsear_fecha_objeto_date_pasa_directo():
    d = date(2026, 5, 22)
    assert parsear_fecha(d) == d


def test_parsear_fecha_iso():
    assert parsear_fecha("2026-05-22") == date(2026, 5, 22)


def test_parsear_fecha_iso_con_timestamp():
    assert parsear_fecha("2026-05-22T10:00:00") == date(2026, 5, 22)


def test_parsear_fecha_iso_invalida():
    assert parsear_fecha("2026-99-99") is None


def test_parsear_fecha_yyyy_slash_mm_slash_dd():
    assert parsear_fecha("2026/05/22") == date(2026, 5, 22)


def test_parsear_fecha_yyyy_slash_invalida():
    assert parsear_fecha("2026/99/99") is None


def test_parsear_fecha_punto_dd_mm_yyyy():
    assert parsear_fecha("22.05.2026") == date(2026, 5, 22)


def test_parsear_fecha_punto_invalida():
    assert parsear_fecha("99.99.2026") is None


def test_parsear_fecha_guion_dd_mm_yyyy():
    assert parsear_fecha("22-05-2026") == date(2026, 5, 22)


def test_parsear_fecha_guion_invalida():
    assert parsear_fecha("99-99-2026") is None


def test_parsear_fecha_dd_mm_yyyy_europeo():
    assert parsear_fecha("22/05/2026") == date(2026, 5, 22)


def test_parsear_fecha_dd_gt_12_fuerza_dd_mm():
    # 22/03/2026 → día 22, mes 3
    assert parsear_fecha("22/03/2026") == date(2026, 3, 22)


def test_parsear_fecha_mm_gt_12_fuerza_mm_dd():
    # 03/22/2026 → mes 3, día 22
    assert parsear_fecha("03/22/2026") == date(2026, 3, 22)


def test_parsear_fecha_ambigua_usa_dd_mm():
    # 5/4/2026 → día 5, mes 4 (contexto europeo)
    assert parsear_fecha("5/4/2026") == date(2026, 4, 5)


def test_parsear_fecha_slash_invalida():
    assert parsear_fecha("99/99/2026") is None


def test_parsear_fecha_yy_2digitos():
    assert parsear_fecha("22/05/26") == date(2026, 5, 22)


def test_parsear_fecha_yy_invalida():
    assert parsear_fecha("99/99/26") is None


def test_parsear_fecha_string_vacio():
    assert parsear_fecha("") is None
    assert parsear_fecha("   ") is None


def test_parsear_fecha_formato_no_reconocido():
    assert parsear_fecha("alguna-cosa") is None
    assert parsear_fecha("2026.05.22") is None  # solo soporta DD.MM.YYYY


# ── parsear_telefono ──────────────────────────────────────────────────────


def test_parsear_telefono_none():
    assert parsear_telefono(None) is None


def test_parsear_telefono_int():
    assert parsear_telefono(34600000001) == "34600000001"


def test_parsear_telefono_float_notacion_cientifica():
    assert parsear_telefono(34600000001.0) == "34600000001"


def test_parsear_telefono_string_normal():
    assert parsear_telefono(" +34600000001 ") == "+34600000001"


def test_parsear_telefono_vacio_o_invalido():
    assert parsear_telefono("") is None
    assert parsear_telefono("+") is None
    assert parsear_telefono("0") is None
    assert parsear_telefono("+0") is None
    assert parsear_telefono("123") is None  # <=5 chars


# ── formatear_fecha_salida ────────────────────────────────────────────────


def test_formatear_fecha_yymmdd():
    assert formatear_fecha_salida(date(2026, 5, 22), "YYMMDD") == "260522"


def test_formatear_fecha_yyyymmdd():
    assert formatear_fecha_salida(date(2026, 5, 22), "YYYYMMDD") == "20260522"


def test_formatear_fecha_dd_slash_mm_slash_yyyy():
    assert formatear_fecha_salida(date(2026, 5, 22), "DD/MM/YYYY") == "22/05/2026"


def test_formatear_fecha_dd_slash_mm_slash_yy():
    assert formatear_fecha_salida(date(2026, 5, 22), "DD/MM/YY") == "22/05/26"


def test_formatear_fecha_mm_slash_dd_slash_yyyy():
    assert formatear_fecha_salida(date(2026, 5, 22), "MM/DD/YYYY") == "05/22/2026"


def test_formatear_fecha_dd_guion_mm_guion_yyyy():
    assert formatear_fecha_salida(date(2026, 5, 22), "DD-MM-YYYY") == "22-05-2026"


def test_formatear_fecha_formato_desconocido_usa_default():
    assert formatear_fecha_salida(date(2026, 5, 22), "FORMATO-RARO") == "260522"


# ── aplicar_plantilla ────────────────────────────────────────────────────


def test_aplicar_plantilla_completa():
    r = aplicar_plantilla(
        "{FECHA} - {APT} - {NOMBRE}",
        date(2026, 5, 22),
        ["A1", "A2"],
        "Juan",
        "YYMMDD",
        ", ",
    )
    assert r == "260522 - A1, A2 - Juan"


def test_aplicar_plantilla_sin_fecha():
    r = aplicar_plantilla(
        "{FECHA}-{NOMBRE}",
        None,
        [],
        "Juan",
        "YYMMDD",
        ", ",
    )
    assert r == "-Juan"


def test_aplicar_plantilla_sin_apartamentos():
    r = aplicar_plantilla(
        "{APT}/{NOMBRE}",
        None,
        [],
        "Juan",
        "YYMMDD",
        ", ",
    )
    assert r == "/Juan"


def test_aplicar_plantilla_strip():
    r = aplicar_plantilla(
        "  {NOMBRE}  ",
        None,
        [],
        "Juan",
        "YYMMDD",
        ", ",
    )
    assert r == "Juan"


# ── agrupar_contactos ────────────────────────────────────────────────────


def test_agrupar_contactos_mismo_nombre_telefono_se_combinan():
    registros = [
        {"nombre": "Juan", "telefono": "+34600000001",
         "checkin_date": date(2026, 5, 22), "apartamentos": ["A1"]},
        {"nombre": "JUAN", "telefono": "+34600000001",
         "checkin_date": date(2026, 5, 20), "apartamentos": ["A2"]},
    ]
    grupos = agrupar_contactos(registros)
    assert len(grupos) == 1
    grupo = grupos[0]
    assert set(grupo.apartamentos) == {"A1", "A2"}
    # toma la fecha más antigua (la más cercana al primero del grupo)
    assert grupo.checkin_date == date(2026, 5, 20)


def test_agrupar_contactos_diferentes_se_mantienen_separados():
    registros = [
        {"nombre": "Juan", "telefono": "+34600000001",
         "checkin_date": None, "apartamentos": []},
        {"nombre": "Ana", "telefono": "+34600000002",
         "checkin_date": None, "apartamentos": []},
    ]
    grupos = agrupar_contactos(registros)
    assert len(grupos) == 2


def test_agrupar_contactos_apartamento_duplicado_no_se_repite():
    registros = [
        {"nombre": "Juan", "telefono": "+34600000001",
         "checkin_date": None, "apartamentos": ["A1"]},
        {"nombre": "Juan", "telefono": "+34600000001",
         "checkin_date": None, "apartamentos": ["A1", "A2"]},
    ]
    grupos = agrupar_contactos(registros)
    assert grupos[0].apartamentos == ["A1", "A2"]


def test_agrupar_contactos_apartamento_vacio_se_ignora():
    registros = [
        {"nombre": "Juan", "telefono": "+34600000001",
         "checkin_date": None, "apartamentos": ["", None, "A1"]},
    ]
    grupos = agrupar_contactos(registros)
    assert grupos[0].apartamentos == ["A1"]


def test_contacto_agrupado_apartamentos_default():
    c = ContactoAgrupado(nombre="J", telefono="+1", checkin_date=None)
    assert c.apartamentos == []
