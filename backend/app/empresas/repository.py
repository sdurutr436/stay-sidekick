"""Repositorio de datos del módulo de empresas."""

import secrets

import bcrypt

from app.empresas.model import Empresa  # noqa: F401
from app.extensions import db


def crear_empresa(nombre: str, email: str) -> Empresa:
    random_pw = secrets.token_urlsafe(32)
    pw_hash = bcrypt.hashpw(random_pw.encode(), bcrypt.gensalt()).decode()
    empresa = Empresa(
        nombre=nombre,
        email=email,
        password_hash=pw_hash,
        herramientas_activas={},
        configuracion={},
        activa=True,
    )
    db.session.add(empresa)
    db.session.commit()
    return empresa
