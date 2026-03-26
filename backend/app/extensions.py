"""Instancias de extensiones Flask (inicializadas en el app factory)."""

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

cors = CORS()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/day", "50/hour"],
    storage_uri="memory://",
)

db = SQLAlchemy()
