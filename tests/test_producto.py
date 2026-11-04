import unittest

from models.producto import Electronico, Libro, Producto
from utils.exceptions import ValidationError


class TestProducto(unittest.TestCase):
    def test_producto_inicializa(self):
        producto = Producto("Teclado", 120.0, 5, "electrónico", producto_id=10)
        self.assertEqual(producto.id, 10)
        self.assertEqual(producto.nombre, "Teclado")

    def test_electronico_hereda_producto(self):
        self.assertTrue(issubclass(Electronico, Producto))

    def test_libro_hereda_producto(self):
        self.assertTrue(issubclass(Libro, Producto))

    def test_str_coherente(self):
        laptop = Electronico("Laptop", 1500, 60, 12, producto_id=1)
        self.assertIn("Laptop", str(laptop))

    def test_precio_electronico_con_igv(self):
        laptop = Electronico("Laptop", 1000, 10, 12, producto_id=3)
        self.assertAlmostEqual(laptop.calcular_precio_final(), 1180.0)

    def test_precio_electronico_descuento_stock(self):
        monitor = Electronico("Monitor", 500, 60, 12, producto_id=4)
        self.assertAlmostEqual(monitor.calcular_precio_final(), 560.5)

    def test_libro_texto_descuento(self):
        libro = Libro("Python", 200, 10, "Ana", True, producto_id=5)
        self.assertAlmostEqual(libro.calcular_precio_final(), 180.0)

    def test_libro_normal_sin_descuento(self):
        libro = Libro("Historia", 200, 10, "Ana", False, producto_id=6)
        self.assertEqual(libro.calcular_precio_final(), 200.0)

    def test_validacion_precio_negativo(self):
        with self.assertRaises(ValidationError):
            Producto("Teclado", -10, 1, "electrónico", producto_id=7)

    def test_validacion_stock_negativo(self):
        with self.assertRaises(ValidationError):
            Producto("Libro", 50, -1, "libro", producto_id=8)

    def test_validacion_categoria_invalida(self):
        with self.assertRaises(ValidationError):
            Producto("Libro", 50, 1, "otro", producto_id=9)
