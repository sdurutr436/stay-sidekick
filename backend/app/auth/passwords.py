"""Utilidades de hashing y verificación de contraseñas con bcrypt.

bcrypt aplica automáticamente un salt aleatorio en cada hash,
por lo que el mismo password produce hashes distintos — esto es correcto.

Uso:
    hash_str = hash_password("miContraseña")   # → almacenar en BD
    ok       = verify_password("miContraseña", hash_str)  # → en login
"""

import bcrypt


def hash_password(plain: str) -> str:
    """Genera un hash bcrypt de la contraseña en texto claro.

    Parameters
    ----------
    plain:
        Contraseña en texto claro (ya sanitizada por LoginSchema).

    Returns
    -------
    str
        Hash bcrypt como string UTF-8, listo para almacenar en BD.
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Compara la contraseña en claro con su hash bcrypt.

    Parameters
    ----------
    plain:
        Contraseña introducida por el usuario (ya sanitizada).
    hashed:
        Hash almacenado en BD.

    Returns
    -------
    bool
        ``True`` si coinciden, ``False`` en caso contrario o si hay error.
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
