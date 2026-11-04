"""Inventario central del sistema TechBook Store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from models.producto import Electronico, Libro, Producto
from utils.exceptions import NotFoundError, ValidationError
from utils.formatters import categoria_titulo, estado_stock
from utils.validators import validar_id


class Inventario:
    """Gestiona el almacenamiento y consulta de productos."""

    def __init__(self, archivo_json: str | None = None):
        self.archivo_json = Path(archivo_json) if archivo_json else Path(__file__).resolve().parent.parent / "data" / "productos.json"
        self.archivo_json.parent.mkdir(parents=True, exist_ok=True)
        self._productos: Dict[int, Producto] = {}
        self.cargar_desde_json()
        if not self._productos:
            self._productos = self._productos_demo()
            self.guardar_en_json()

    def _productos_demo(self) -> Dict[int, Producto]:
        productos = {
            1: Electronico("Laptop Lenovo IdeaPad", 2800.00, 65, 12, producto_id=1),
            2: Electronico("Monitor Full HD 24\"", 650.00, 15, 24, producto_id=2),
            3: Electronico("Audífonos inalámbricos", 280.00, 0, 12, producto_id=3),
            4: Electronico("Teclado mecánico RGB", 240.00, 7, 18, producto_id=4),
            5: Libro("Python para principiantes", 120.00, 30, "Ana Gómez", True, producto_id=5),
            6: Libro("Clean Code", 140.00, 18, "Robert C. Martin", False, producto_id=6),
            7: Libro("Fundamentos de algoritmos", 180.00, 12, "Luis Torres", True, producto_id=7),
            8: Libro("Desarrollo de aplicaciones web", 160.00, 0, "María Pérez", False, producto_id=8),
        }
        return productos

    def agregar_producto(self, producto: Producto) -> Producto:
        if not isinstance(producto, (Electronico, Libro, Producto)):
            raise ValidationError("El producto no tiene una estructura válida.")
        producto_id = producto.id
        if producto_id is None:
            producto_id = self._generar_id()
            producto.id = producto_id
        if producto_id in self._productos:
            raise ValidationError(f"El ID {producto_id} ya existe en el inventario.")
        self._productos[producto_id] = producto
        self.guardar_en_json()
        return producto

    def _generar_id(self) -> int:
        if not self._productos:
            return 1
        return max(self._productos.keys()) + 1

    def buscar_por_id(self, producto_id: int) -> Producto:
        ident = validar_id(producto_id)
        if ident not in self._productos:
            raise NotFoundError(f"No existe un producto con el ID {ident}.")
        return self._productos[ident]

    def descontar_stock(self, producto_id: int, cantidad: int) -> Producto:
        """Descuenta unidades tras validar disponibilidad y persiste el cambio."""
        ident = validar_id(producto_id)
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValidationError("La cantidad de compra debe ser un entero mayor que cero.")

        producto = self.buscar_por_id(ident)
        if cantidad > producto.stock:
            raise ValidationError(
                f"Solo hay {producto.stock} unidades disponibles de {producto.nombre}."
            )

        stock_anterior = producto.stock
        producto.stock -= cantidad
        try:
            self.guardar_en_json()
        except OSError:
            producto.stock = stock_anterior
            raise
        return producto

    def listar_productos(self) -> List[Producto]:
        return list(self._productos.values())

    def total_productos(self) -> int:
        return len(self._productos)

    def obtener_estadisticas(self) -> dict:
        productos = self.listar_productos()
        electronicos = sum(1 for item in productos if item.categoria == "electrónico")
        libros = sum(1 for item in productos if item.categoria == "libro")
        sin_stock = sum(1 for item in productos if item.stock == 0)
        return {
            "total": len(productos),
            "electronicos": electronicos,
            "libros": libros,
            "sin_stock": sin_stock,
        }

    def guardar_en_json(self) -> None:
        datos = [producto.to_dict() for producto in self._productos.values()]
        with open(self.archivo_json, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)

    def cargar_desde_json(self) -> None:
        if not self.archivo_json.exists():
            return
        try:
            with open(self.archivo_json, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return

        if not isinstance(datos, list):
            return

        self._productos = {}
        for item in datos:
            try:
                if item.get("tipo") == "electronico":
                    producto = Electronico(
                        nombre=item["nombre"],
                        precio_base=item["precio_base"],
                        stock=item["stock"],
                        garantia_meses=item.get("garantia_meses", 0),
                        producto_id=item.get("id"),
                    )
                elif item.get("tipo") == "libro":
                    producto = Libro(
                        nombre=item["nombre"],
                        precio_base=item["precio_base"],
                        stock=item["stock"],
                        autor=item["autor"],
                        es_libro_texto=item.get("es_libro_texto", False),
                        producto_id=item.get("id"),
                    )
                else:
                    continue
                self._productos[producto.id] = producto
            except (KeyError, TypeError, ValidationError):
                continue

    def filtrar_productos(self, texto: str = "", categoria: str = "todos") -> List[Producto]:
        busqueda = (texto or "").strip().lower()
        resultados = []
        for producto in self.listar_productos():
            categoria_ok = categoria == "todos" or producto.categoria == categoria
            texto_ok = True
            if busqueda:
                texto_normal = "".join(ch for ch in busqueda if ch.isalnum() or ch.isspace())
                hay_coincidencia = (
                    texto_normal in producto.nombre.lower().replace("á", "a").replace("é", "e")
                    or (
                        isinstance(producto, Libro)
                        and texto_normal in producto.autor.lower().replace("á", "a").replace("é", "e")
                    )
                    or texto_normal in categoria_titulo(producto.categoria).lower()
                    or str(producto.id) in busqueda
                )
                texto_ok = hay_coincidencia
            if categoria_ok and texto_ok:
                resultados.append(producto)
        return resultados

    def estado_producto(self, producto: Producto) -> str:
        return estado_stock(producto.stock)
