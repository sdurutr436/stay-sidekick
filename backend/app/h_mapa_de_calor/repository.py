"""Repositorio del mapa de calor.

Solo gestiona configuración de umbrales y columnas XLSX en
empresas.configuracion["heatmap"] (JSONB). No persiste datos de reservas.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.empresas.model import Empresa
from app.extensions import db
from app.h_maestro_apartamentos.repository import create_sync_log  # noqa: F401

_DEFAULTS_UMBRALES = {"nivel1": 10, "nivel2": 20, "nivel3": 30}


# ── Empresa ───────────────────────────────────────────────────────────────


def get_empresa(empresa_id: str) -> Empresa | None:
    return Empresa.query.filter_by(id=empresa_id).first()


# ── Umbrales ──────────────────────────────────────────────────────────────


def get_umbrales(empresa_id: str) -> dict:
    """Lee los umbrales del JSONB. Devuelve defaults si no están configurados."""
    empresa = get_empresa(empresa_id)
    if empresa is None:
        return dict(_DEFAULTS_UMBRALES)
    heatmap = (empresa.configuracion or {}).get("heatmap", {})
    return heatmap.get("umbrales", dict(_DEFAULTS_UMBRALES))


def save_umbrales(empresa_id: str, umbrales: dict) -> dict:
    """Persiste los umbrales en empresas.configuracion["heatmap"]["umbrales"]."""
    empresa = get_empresa(empresa_id)
    cfg = dict(empresa.configuracion or {})
    heatmap = dict(cfg.get("heatmap", {}))
    heatmap["umbrales"] = umbrales
    cfg["heatmap"] = heatmap
    empresa.configuracion = cfg
    empresa.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return umbrales


# ── Configuración XLSX ────────────────────────────────────────────────────


def get_config_xlsx(empresa_id: str) -> dict:
    """Lee col_fecha_checkin y col_fecha_checkout del JSONB. Devuelve None si no están."""
    empresa = get_empresa(empresa_id)
    if empresa is None:
        return {"col_fecha_checkin": None, "col_fecha_checkout": None}
    heatmap = (empresa.configuracion or {}).get("heatmap", {})
    return {
        "col_fecha_checkin": heatmap.get("col_fecha_checkin"),
        "col_fecha_checkout": heatmap.get("col_fecha_checkout"),
    }


def save_config_xlsx(
    empresa_id: str,
    col_fecha_checkin: str,
    col_fecha_checkout: str | None,
) -> dict:
    """Persiste col_fecha_checkin y col_fecha_checkout en el JSONB de la empresa."""
    empresa = get_empresa(empresa_id)
    cfg = dict(empresa.configuracion or {})
    heatmap = dict(cfg.get("heatmap", {}))
    heatmap["col_fecha_checkin"] = col_fecha_checkin
    heatmap["col_fecha_checkout"] = col_fecha_checkout
    cfg["heatmap"] = heatmap
    empresa.configuracion = cfg
    empresa.updated_at = datetime.now(timezone.utc)
    db.session.flush()
    return {"col_fecha_checkin": col_fecha_checkin, "col_fecha_checkout": col_fecha_checkout}
