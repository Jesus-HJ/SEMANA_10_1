"""Aplicación CLI de TechBook Store."""

from __future__ import annotations

from models.inventario import Inventario
from models.producto import Electronico, Libro
from utils.exceptions import NotFoundError, ValidationError
from utils.formatters import formatear_moneda


class TechBookCLI:
    """Controlador de la interfaz de línea de comandos."""

    def __init__(self):
        self.inventario = Inventario(r"D:\VSC\SEMANA_10_1\data\productos.json")

    def agregar_producto(self) -> None:
        print("\nTipo de producto: 1) Electrónico  2) Libro")
        tipo = input("Seleccione tipo: ").strip()
        if tipo not in {"1", "2"}:
            raise ValidationError("Tipo de producto inválido.")

        nombre = input("Nombre: ").strip()
        precio = float(input("Precio base: ").strip())
        stock = int(input("Stock: ").strip())

        if tipo == "1":
            garantia = int(input("Garantía (meses): ").strip())
            producto = Electronico(
                nombre=nombre,
                precio_base=precio,
                stock=stock,
                garantia_meses=garantia,
            )
        else:
            autor = input("Autor: ").strip()
            libro_texto = input("¿Es libro de texto? (s/n): ").strip().lower() == "s"
            producto = Libro(
                nombre=nombre,
                precio_base=precio,
                stock=stock,
                autor=autor,
                es_libro_texto=libro_texto,
            )

        self.inventario.agregar_producto(producto)
        print(f"Producto registrado correctamente. ID: {producto.id}")

    def listar_productos(self) -> None:
        productos = self.inventario.listar_productos()
        if not productos:
            print("\nEl inventario está vacío.")
            return

        print("\n=== INVENTARIO ===")
        for producto in productos:
            print(producto)
            print("-" * 60)

    def calcular_precio_final(self) -> None:
        ident = input("Ingrese el ID del producto: ").strip()
        try:
            producto_id = int(ident)
        except ValueError as exc:
            raise ValidationError("El ID debe ser numérico.") from exc

        producto = self.inventario.buscar_por_id(producto_id)
        precio_final = producto.calcular_precio_final()
        print(f"\nProducto: {producto.nombre}")
        print(f"Categoría: {producto.categoria}")
        print(f"Precio base: {formatear_moneda(producto.precio_base)}")
        print(f"Regla aplicada: {producto.regla_precio()}")
        print(f"Precio final: {formatear_moneda(precio_final)}")

    def ejecutar(self) -> None:
        while True:
            print("\n====================================")
            print("     TECHBOOK STORE - SISTEMA CLI")
            print("====================================")
            print("1. Agregar producto")
            print("2. Listar productos")
            print("3. Calcular precio final")
            print("4. Salir")

            opcion = input("Seleccione una opción: ").strip()

            try:
                if opcion == "1":
                    self.agregar_producto()
                elif opcion == "2":
                    self.listar_productos()
                elif opcion == "3":
                    self.calcular_precio_final()
                elif opcion == "4":
                    print("\nGracias por visitar TechBook Store. ¡Hasta luego!")
                    break
                else:
                    raise ValidationError("Opción no válida. Intente nuevamente.")
            except (ValidationError, NotFoundError) as exc:
                print(f"\nError: {exc}")
            except Exception as exc:  # pragma: no cover
                print(f"\nOcurrió un error inesperado: {exc}")


if __name__ == "__main__":
    TechBookCLI().ejecutar()
