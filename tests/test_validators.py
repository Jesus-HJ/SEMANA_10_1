import unittest

from utils.exceptions import ValidationError
from utils.validators import validar_categoria, validar_nombre, validar_precio, validar_stock


class TestValidators(unittest.TestCase):
    def test_nombre_valido(self):
        self.assertEqual(validar_nombre("Python"), "Python")

    def test_nombre_vacio(self):
        with self.assertRaises(ValidationError):
            validar_nombre("   ")

    def test_precio_valido(self):
        self.assertEqual(validar_precio(50), 50.0)

    def test_precio_invalido(self):
        with self.assertRaises(ValidationError):
            validar_precio(-1)

    def test_stock_valido(self):
        self.assertEqual(validar_stock(5), 5)

    def test_stock_invalido(self):
        with self.assertRaises(ValidationError):
            validar_stock(-2)

    def test_categoria_valida(self):
        self.assertEqual(validar_categoria("libro"), "libro")

    def test_categoria_invalida(self):
        with self.assertRaises(ValidationError):
            validar_categoria("otro")
