"""Validaciones del dominio TechBook Store."""

from __future__ import annotations

from utils.exceptions import ValidationError

VALID_CATEGORIAS = {"electrónico", "electronico", "electrónicos", "electronicos", "libro", "libros"}


def validar_nombre(nombre: str) -> str:
    if not isinstance(nombre, str) or not nombre.strip():
        raise ValidationError("El nombre no puede estar vacío.")
    return nombre.strip()


def validar_precio(precio: float) -> float:
    try:
        valor = float(precio)
    except (TypeError, ValueError) as exc:
        raise ValidationError("El precio debe ser un valor numérico válido.") from exc
    if valor <= 0:
        raise ValidationError("El precio debe ser mayor que cero.")
    return valor


def validar_stock(stock: int) -> int:
    if not isinstance(stock, int):
        raise ValidationError("El stock debe ser un entero válido.")
    if stock < 0:
        raise ValidationError("El stock no puede ser negativo.")
    return stock


def validar_garantia(garantia: int) -> int:
    if not isinstance(garantia, int):
        raise ValidationError("La garantía debe ser un entero válido.")
    if garantia < 0:
        raise ValidationError("La garantía no puede ser negativa.")
    return garantia


def validar_autor(autor: str) -> str:
    if not isinstance(autor, str) or not autor.strip():
        raise ValidationError("El autor no puede estar vacío.")
    return autor.strip()


def validar_categoria(categoria: str) -> str:
    if not isinstance(categoria, str) or not categoria.strip():
        raise ValidationError("La categoría es obligatoria.")
    categoria_normalizada = categoria.strip().lower()
    if categoria_normalizada in {"electrónico", "electronico", "electrónicos", "electronicos"}:
        return "electrónico"
    if categoria_normalizada in {"libro", "libros"}:
        return "libro"
    raise ValidationError("La categoría no es válida.")


def validar_id(producto_id: int) -> int:
    try:
        valor = int(producto_id)
    except (TypeError, ValueError) as exc:
        raise ValidationError("El ID del producto debe ser numérico.") from exc
    if valor <= 0:
        raise ValidationError("El ID debe ser un entero positivo.")
    return valor


def validar_opcion_menu(opcion: str) -> str:
    if opcion not in {"1", "2", "3", "4"}:
        raise ValidationError("La opción del menú no es válida.")
    return opcion
