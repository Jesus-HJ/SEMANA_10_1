"""Mixin reutilizable para descuentos."""

from __future__ import annotations


class DescuentoMixin:
    """Mixin que centraliza la lógica de descuento aplicable a productos."""

    @staticmethod
    def aplicar_descuento(precio: float, porcentaje: float) -> float:
        return precio * (1 - porcentaje)
