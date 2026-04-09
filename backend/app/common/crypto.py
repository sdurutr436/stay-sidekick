"""Utilidades de cifrado simétrico con Fernet.

Usado para cifrar/descifrar API keys almacenadas en BD
(configuracion_pms, configuracion_ia, integraciones_google).

La clave Fernet se carga desde la variable de entorno FERNET_KEY.
Generarla con:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""

import logging

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Obtiene la instancia Fernet a partir de la clave configurada."""
    key = current_app.config["FERNET_KEY"]
    if not key:
        raise RuntimeError("FERNET_KEY no configurada. Genera una con: "
                           "python -c \"from cryptography.fernet import Fernet; "
                           "print(Fernet.generate_key().decode())\"")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(plaintext: str) -> str:
    """Cifra un texto plano y devuelve el token Fernet como string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str | None:
    """Descifra un token Fernet. Devuelve None si el token es inválido."""
    f = _get_fernet()
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        logger.error("Token Fernet inválido — posible clave incorrecta o dato corrupto")
        return None
