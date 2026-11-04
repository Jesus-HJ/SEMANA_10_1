import tempfile
import unittest
from pathlib import Path

from models.inventario import Inventario
from models.producto import Electronico, Libro
from utils.exceptions import NotFoundError, ValidationError


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        data_path = Path(self.temporary_directory.name) / "productos.json"
        self.inventario = Inventario(str(data_path))
        self.inventario._productos = {}

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_agregar_producto(self):
        laptop = Electronico("Laptop", 1000, 10, 12, producto_id=1)
        self.inventario.agregar_producto(laptop)
        self.assertEqual(self.inventario.total_productos(), 1)

    def test_buscar_producto_por_id(self):
        libro = Libro("Python", 200, 3, "Ana", True, producto_id=2)
        self.inventario.agregar_producto(libro)
        resultado = self.inventario.buscar_por_id(2)
        self.assertEqual(resultado.nombre, "Python")

    def test_id_duplicado(self):
        laptop = Electronico("Laptop", 1000, 10, 12, producto_id=1)
        self.inventario.agregar_producto(laptop)
        with self.assertRaises(ValidationError):
            self.inventario.agregar_producto(Electronico("Otro", 1000, 10, 12, producto_id=1))

    def test_buscar_inexistente(self):
        with self.assertRaises(NotFoundError):
            self.inventario.buscar_por_id(99)

    def test_filtro_por_categoria(self):
        self.inventario.agregar_producto(Electronico("Laptop", 1000, 10, 12, producto_id=1))
        self.inventario.agregar_producto(Libro("Python", 150, 5, "Ana", True, producto_id=2))
        resultados = self.inventario.filtrar_productos(categoria="libro")
        self.assertEqual(len(resultados), 1)
