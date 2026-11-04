"""Excepciones personalizadas del proyecto."""


class ValidationError(Exception):
    """Se eleva cuando los datos de entrada son inválidos."""


class NotFoundError(Exception):
    """Se eleva cuando un recurso no existe en el inventario."""
