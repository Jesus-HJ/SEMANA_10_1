import tempfile
import unittest
from pathlib import Path

import app as app_module
from models.inventario import Inventario


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        data_path = Path(self.temporary_directory.name) / "productos.json"
        sales_path = Path(self.temporary_directory.name) / "ventas.json"
        self.original_inventory = app_module.inventario
        self.original_sales = app_module.ventas
        app_module.inventario = Inventario(str(data_path))
        app_module.ventas = app_module.RegistroVentas(str(sales_path))
        self.client = app_module.app.test_client()

    def login_admin(self, username="admin", password="admin"):
        return self.client.post(
            "/admin/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def tearDown(self):
        app_module.inventario = self.original_inventory
        app_module.ventas = self.original_sales
        self.temporary_directory.cleanup()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TechBook Store", response.data)
        self.assertIn("Área de clientes", response.get_data(as_text=True))

    def test_area_clientes(self):
        response = self.client.get("/clientes")
        self.assertEqual(response.status_code, 200)
        contenido = response.get_data(as_text=True)
        self.assertIn("Clientes | TechBook Store", contenido)
        self.assertIn("Área de clientes", contenido)

    def test_detalle(self):
        response = self.client.get("/producto/1")
        self.assertEqual(response.status_code, 200)

    def test_producto_inexistente(self):
        response = self.client.get("/producto/9999")
        self.assertEqual(response.status_code, 404)

    def test_admin(self):
        self.login_admin()
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Área del administrador", response.get_data(as_text=True))
        contenido = response.get_data(as_text=True)
        self.assertIn("Opciones del administrador", contenido)
        self.assertIn("Salir", contenido)
        self.assertNotIn("Ir al área de clientes", contenido)

    def test_admin_no_puede_comprar(self):
        self.login_admin()
        stock_inicial = app_module.inventario.buscar_por_id(2).stock
        response = self.client.post(
            "/comprar/2",
            data={
                "nombre_cliente": "Administrador",
                "correo": "admin@example.com",
                "cantidad": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.headers["Location"])
        self.assertEqual(app_module.inventario.buscar_por_id(2).stock, stock_inicial)
        self.assertEqual(app_module.ventas.listar(), [])

    def test_admin_no_ve_formulario_de_compra(self):
        self.login_admin()
        response = self.client.get("/producto/2")
        contenido = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('id="compra"', contenido)
        self.assertNotIn("Confirmar compra", contenido)
        self.assertIn("Las compras están deshabilitadas", contenido)

    def test_catalogo_admin_no_muestra_accion_de_compra(self):
        self.login_admin()
        response = self.client.get("/clientes")
        contenido = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Ver y comprar", contenido)
        self.assertIn("Ver detalle", contenido)

    def test_navbar_no_muestra_enlace_clientes(self):
        response = self.client.get("/")
        contenido = response.get_data(as_text=True)
        self.assertNotIn(">Clientes</a>", contenido)

    def test_admin_requiere_autenticacion(self):
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_registrar_producto_requiere_autenticacion(self):
        response = self.client.post(
            "/admin/productos",
            data={
                "tipo": "libro",
                "nombre": "No autorizado",
                "precio_base": "50",
                "stock": "1",
                "autor": "Autor",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])
        self.assertEqual(app_module.inventario.total_productos(), 8)

    def test_login_admin_correcto(self):
        response = self.login_admin()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Gestión de inventario", response.get_data(as_text=True))

    def test_login_admin_incorrecto(self):
        response = self.client.post(
            "/admin/login",
            data={"username": "admin", "password": "incorrecta"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Usuario o contraseña incorrectos", response.get_data(as_text=True))
        with self.client.session_transaction() as session:
            self.assertFalse(session.get("admin_authenticated", False))

    def test_logout_admin(self):
        self.login_admin()
        response = self.client.post("/admin/logout")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/clientes", response.headers["Location"])
        admin_response = self.client.get("/admin")
        self.assertEqual(admin_response.status_code, 302)

    def test_compra_actualiza_stock_y_aparece_en_admin(self):
        response = self.client.post(
            "/comprar/2",
            data={
                "nombre_cliente": "Cliente Demo",
                "correo": "cliente@example.com",
                "cantidad": "3",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(app_module.inventario.buscar_por_id(2).stock, 12)
        self.assertIn("Compra #1 confirmada", response.get_data(as_text=True))

        self.login_admin()
        admin_response = self.client.get("/admin")
        admin_content = admin_response.get_data(as_text=True)
        self.assertIn("Ventas registradas", admin_content)
        self.assertIn("Monitor Full HD", admin_content)
        self.assertIn("12", admin_content)
        self.assertNotIn("Cliente Demo", admin_content)
        self.assertNotIn("cliente@example.com", admin_content)

    def test_compra_rechaza_cantidad_mayor_al_stock(self):
        response = self.client.post(
            "/comprar/2",
            data={
                "nombre_cliente": "Cliente Demo",
                "correo": "cliente@example.com",
                "cantidad": "16",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(app_module.inventario.buscar_por_id(2).stock, 15)
        self.assertEqual(app_module.ventas.listar(), [])

    def test_compra_rechaza_producto_agotado(self):
        response = self.client.post(
            "/comprar/3",
            data={
                "nombre_cliente": "Cliente Demo",
                "correo": "cliente@example.com",
                "cantidad": "1",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(app_module.ventas.listar(), [])

    def test_registro_valido(self):
        self.login_admin()
        response = self.client.post(
            "/admin/productos",
            data={
                "tipo": "libro",
                "nombre": "Nuevo libro",
                "precio_base": "90",
                "stock": "12",
                "autor": "Autor nuevo",
                "es_libro_texto": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
