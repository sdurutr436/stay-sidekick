"""Tests del parser de XLSX de apartamentos."""

from io import BytesIO

from openpyxl import Workbook

from app.h_maestro_apartamentos.xlsx_parser import (
    XlsxApartment,
    _build_col_map_from_headers,
    _build_col_map_from_override,
    _should_use_override,
    parse_xlsx,
)


def _build_xlsx(rows: list[tuple]) -> bytes:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── parse_xlsx ────────────────────────────────────────────────────────────


def test_parse_xlsx_archivo_invalido():
    apts, errors = parse_xlsx(b"not-xlsx")
    assert apts == []
    assert "abrir" in errors[0].lower()


def test_parse_xlsx_solo_cabecera():
    xlsx = _build_xlsx([("id", "nombre")])
    apts, errors = parse_xlsx(xlsx)
    assert apts == []
    assert errors


def test_parse_xlsx_sin_columna_id():
    xlsx = _build_xlsx([
        ("nombre", "direccion"),
        ("A1", "Calle 1"),
    ])
    apts, errors = parse_xlsx(xlsx)
    assert apts == []
    assert any("ID" in e for e in errors)


def test_parse_xlsx_sin_columna_nombre():
    xlsx = _build_xlsx([
        ("id", "direccion"),
        ("1001", "Calle 1"),
    ])
    apts, errors = parse_xlsx(xlsx)
    assert apts == []
    assert any("nombre" in e.lower() for e in errors)


def test_parse_xlsx_modo_cabecera_ok():
    xlsx = _build_xlsx([
        ("id", "nombre", "direccion", "ciudad"),
        ("1001", "A1", "Calle 1", "Cádiz"),
        ("1002", "A2", "Calle 2", "Madrid"),
    ])
    apts, errors = parse_xlsx(xlsx)
    assert errors == []
    assert len(apts) == 2
    assert apts[0].nombre == "A1"
    assert apts[1].ciudad == "Madrid"


def test_parse_xlsx_fila_sin_id_se_omite():
    xlsx = _build_xlsx([
        ("id", "nombre"),
        ("", "A1"),
        ("1002", "A2"),
    ])
    apts, errors = parse_xlsx(xlsx)
    assert len(apts) == 1
    assert apts[0].nombre == "A2"
    assert errors


def test_parse_xlsx_fila_sin_nombre_se_omite():
    xlsx = _build_xlsx([
        ("id", "nombre"),
        ("1001", ""),
        ("1002", "A2"),
    ])
    apts, errors = parse_xlsx(xlsx)
    assert len(apts) == 1


def test_parse_xlsx_con_override():
    # XLSX con cabeceras desconocidas → solo override funcionará
    xlsx = _build_xlsx([
        ("col1", "col2", "col3"),  # cabeceras irrelevantes
        ("id-1", "ID-EXT-1", "Apt 1"),
        ("id-2", "ID-EXT-2", "Apt 2"),
    ])
    override = {"col_id_externo": 2, "col_nombre": 3}
    apts, errors = parse_xlsx(xlsx, col_override=override)
    assert errors == []
    assert len(apts) == 2
    assert apts[0].id_pms == "id-1"
    assert apts[0].id_externo == "ID-EXT-1"


def test_parse_xlsx_id_pms_siempre_columna_1():
    """id_pms se toma siempre de columna A, independiente de col_override."""
    xlsx = _build_xlsx([
        ("a", "b", "c"),
        ("1001", "EXT-9", "Apt-1"),
    ])
    apts, _ = parse_xlsx(xlsx, col_override={"col_id_externo": 2, "col_nombre": 3})
    assert apts[0].id_pms == "1001"
    assert apts[0].id_externo == "EXT-9"
    assert apts[0].nombre == "Apt-1"


# ── _should_use_override ──────────────────────────────────────────────────


def test_should_use_override_none():
    assert _should_use_override(None) is False


def test_should_use_override_vacio():
    assert _should_use_override({}) is False


def test_should_use_override_solo_uno_configurado():
    assert _should_use_override({"col_id_externo": 1}) is False
    assert _should_use_override({"col_nombre": 1}) is False


def test_should_use_override_ambos_configurados():
    assert _should_use_override({"col_id_externo": 2, "col_nombre": 3}) is True


def test_should_use_override_cero_es_no_configurado():
    assert _should_use_override({"col_id_externo": 0, "col_nombre": 3}) is False


# ── _build_col_map_from_override ─────────────────────────────────────────


def test_build_col_map_from_override_simple():
    m = _build_col_map_from_override({
        "col_id_externo": 1,
        "col_nombre": 2,
    })
    assert m == {0: "id_externo", 1: "nombre"}


def test_build_col_map_from_override_con_opcionales():
    m = _build_col_map_from_override({
        "col_id_externo": 2,
        "col_nombre": 3,
        "col_direccion": 4,
        "col_ciudad": 5,
    })
    assert m == {1: "id_externo", 2: "nombre", 3: "direccion", 4: "ciudad"}


def test_build_col_map_from_override_ignora_ceros():
    m = _build_col_map_from_override({
        "col_id_externo": 1,
        "col_nombre": 2,
        "col_direccion": 0,
    })
    assert "direccion" not in m.values()


# ── _build_col_map_from_headers ──────────────────────────────────────────


def test_build_col_map_from_headers_ok():
    m, errors = _build_col_map_from_headers(("id", "nombre", "direccion"))
    assert errors == []
    assert m[0] == "id_externo"
    assert m[1] == "nombre"
    assert m[2] == "direccion"


def test_build_col_map_from_headers_aliases():
    m, errors = _build_col_map_from_headers(("identificador", "name", "address", "city"))
    assert errors == []
    assert set(m.values()) == {"id_externo", "nombre", "direccion", "ciudad"}


def test_build_col_map_from_headers_sin_id():
    m, errors = _build_col_map_from_headers(("nombre",))
    assert any("ID" in e for e in errors)


def test_build_col_map_from_headers_sin_nombre():
    m, errors = _build_col_map_from_headers(("id",))
    assert any("nombre" in e.lower() for e in errors)


def test_build_col_map_from_headers_cabecera_none_se_salta():
    m, errors = _build_col_map_from_headers(("id", None, "nombre"))
    assert errors == []
    assert m[0] == "id_externo"
    assert m[2] == "nombre"


# ── XlsxApartment dataclass ───────────────────────────────────────────────


def test_xlsx_apartment_dataclass():
    apt = XlsxApartment(
        id_pms="1001", id_externo="ext-1", nombre="A1",
        direccion="D1", ciudad="C",
    )
    assert apt.id_pms == "1001"
