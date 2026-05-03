"""Utilidades para conversión de letras de columna Excel a índice numérico."""


def col_letra_a_indice(letra: str) -> int:
    """Convierte una letra de columna estilo Excel a índice 0-based.

    "A" -> 0, "B" -> 1, ..., "Z" -> 25, "AA" -> 26, etc.

    Parameters
    ----------
    letra:
        Letra(s) de columna en notación Excel (case-insensitive).

    Raises
    ------
    ValueError
        Si ``letra`` es None o vacía.
    """
    if not letra:
        raise ValueError("La letra de columna no puede estar vacía.")
    letra = letra.upper()
    result = 0
    for ch in letra:
        result = result * 26 + (ord(ch) - ord("A") + 1)
    return result - 1
