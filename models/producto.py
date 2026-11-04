"""Modelos del dominio de productos."""

from __future__ import annotations

from models.mixins import DescuentoMixin
from utils.exceptions import ValidationError
from utils.formatters import categoria_titulo
from utils.validators import (
    validar_autor,
    validar_categoria,
    validar_garantia,
    validar_id,
    validar_nombre,
    validar_precio,
    validar_stock,
)


class Producto:
    """Representa cualquier producto del catálogo."""

    def __init__(self, nombre: str, precio_base: float, stock: int, categoria: str, producto_id: int | None = None):
        self._id = validar_id(producto_id) if producto_id is not None else None
        self.nombre = nombre
        self.precio_base = precio_base
        self.stock = stock
        self.categoria = categoria

    @property
    def id(self) -> int | None:
        return self._id

    @id.setter
    def id(self, value: int | None) -> None:
        if value is None:
            self._id = None
            return
        self._id = validar_id(value)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        self._nombre = validar_nombre(value)

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, value: float) -> None:
        self._precio_base = validar_precio(value)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value: int) -> None:
        self._stock = validar_stock(value)

    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, value: str) -> None:
        self._categoria = validar_categoria(value)

    def calcular_precio_final(self) -> float:
        return float(self.precio_base)

    def regla_precio(self) -> str:
        return "Sin descuento adicional"

    def __str__(self) -> str:
        return (
            f"ID: {self.id} | Tipo: {categoria_titulo(self.categoria)} | "
            f"Nombre: {self.nombre} | Precio base: S/ {self.precio_base:.2f} | "
            f"Stock: {self.stock}"
        )

    def __del__(self) -> None:
        try:
            print(f"Producto {self.nombre} liberado de la memoria.")
        except Exception:  # pragma: no cover
            pass

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio_base": self.precio_base,
            "stock": self.stock,
            "categoria": self.categoria,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        tipo = data.get("tipo", "produto")
        if tipo == "electronico":
            return Electronico(
                nombre=data["nombre"],
                precio_base=data["precio_base"],
                stock=data["stock"],
                garantia_meses=data["garantia_meses"],
                producto_id=data.get("id"),
            )
        if tipo == "libro":
            return Libro(
                nombre=data["nombre"],
                precio_base=data["precio_base"],
                stock=data["stock"],
                autor=data["autor"],
                es_libro_texto=data.get("es_libro_texto", False),
                producto_id=data.get("id"),
            )
        return cls(
            nombre=data["nombre"],
            precio_base=data["precio_base"],
            stock=data["stock"],
            categoria=data.get("categoria", "libro"),
            producto_id=data.get("id"),
        )


class Electronico(DescuentoMixin, Producto):
    """Producto electrónico con IGV y descuento por stock."""

    DESCUENTO_STOCK = 0.05

    def __init__(self, nombre: str, precio_base: float, stock: int, garantia_meses: int, producto_id: int | None = None):
        super().__init__(nombre, precio_base, stock, "electrónico", producto_id)
        self.garantia_meses = garantia_meses

    @property
    def garantia_meses(self) -> int:
        return self._garantia_meses

    @garantia_meses.setter
    def garantia_meses(self, value: int) -> None:
        self._garantia_meses = validar_garantia(value)

    def calcular_precio_final(self) -> float:
        precio = self.precio_base * 1.18
        if self.stock > 50:
            precio = self.aplicar_descuento(precio, self.DESCUENTO_STOCK)
        return round(precio, 2)

    def regla_precio(self) -> str:
        if self.stock > 50:
            return "IGV + descuento por stock mayor a 50 unidades (5%)"
        return "IGV aplicado (18%)"

    def __str__(self) -> str:
        return f"{super().__str__()} | Garantía: {self.garantia_meses} meses"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"tipo": "electronico", "garantia_meses": self.garantia_meses})
        return data


class Libro(DescuentoMixin, Producto):
    """Libro con posibilidad de descuento por texto académico."""

    def __init__(self, nombre: str, precio_base: float, stock: int, autor: str, es_libro_texto: bool = False, producto_id: int | None = None):
        super().__init__(nombre, precio_base, stock, "libro", producto_id)
        self.autor = autor
        self.es_libro_texto = es_libro_texto

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, value: str) -> None:
        self._autor = validar_autor(value)

    @property
    def es_libro_texto(self) -> bool:
        return self._es_libro_texto

    @es_libro_texto.setter
    def es_libro_texto(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValidationError("El indicador de libro de texto debe ser booleano.")
        self._es_libro_texto = value

    def calcular_precio_final(self) -> float:
        if self.es_libro_texto:
            return round(self.aplicar_descuento(self.precio_base, 0.10), 2)
        return round(float(self.precio_base), 2)

    def regla_precio(self) -> str:
        if self.es_libro_texto:
            return "Descuento de libro de texto (10%)"
        return "Sin descuento aplicado"

    def __str__(self) -> str:
        texto = "Texto académico" if self.es_libro_texto else "General"
        return f"{super().__str__()} | Autor: {self.autor} | Tipo de libro: {texto}"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"tipo": "libro", "autor": self.autor, "es_libro_texto": self.es_libro_texto})
        return data


if __name__ == "__main__":
    print(Producto.__mro__)
    print(Electronico.__mro__)
    print(Libro.__mro__)
