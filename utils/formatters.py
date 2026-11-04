"""Funciones de presentación para la interfaz del proyecto."""

from __future__ import annotations


def formatear_moneda(valor: float) -> str:
    return f"S/ {float(valor):.2f}"


def estado_stock(stock: int) -> str:
    return "Disponible" if stock > 0 else "Agotado"


def categoria_titulo(categoria: str) -> str:
    categoria = (categoria or "").strip().lower()
    if categoria in {"electrónico", "electronico", "electrónicos", "electronicos"}:
        return "Electrónico"
    if categoria in {"libro", "libros"}:
        return "Libro"
    return categoria.title()
