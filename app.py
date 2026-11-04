"""Aplicación web Flask para TechBook Store."""

from __future__ import annotations

import hmac
import os
import secrets
from functools import wraps
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for

from models.inventario import Inventario
from models.producto import Electronico, Libro, Producto
from models.ventas import RegistroVentas
from utils.exceptions import NotFoundError, ValidationError
from utils.formatters import formatear_moneda
from utils.validators import validar_nombre

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("TECHBOOK_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["JSON_SORT_KEYS"] = False
DATA_PATH = Path(__file__).resolve().parent / "data" / "productos.json"
inventario = Inventario(str(DATA_PATH))
ventas = RegistroVentas(str(DATA_PATH.with_name("ventas.json")))
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

PRODUCT_IMAGES = {
    1: "images/laptop.jpg",
    2: "images/monitor.jpg",
    3: "images/headphones.jpg",
    4: "images/keyboard.jpg",
    5: "images/algorithms-book.jpg",
    6: "images/clean-code.jpg",
    7: "images/algorithms-book.jpg",
    8: "images/clean-code.jpg",
}
DEFAULT_IMAGES = {
    "electrónico": "images/monitor.jpg",
    "libro": "images/algorithms-book.jpg",
}


def product_image(producto: Producto) -> str:
    """Devuelve una imagen local para el producto, con alternativa por categoría."""
    filename = PRODUCT_IMAGES.get(producto.id, DEFAULT_IMAGES[producto.categoria])
    return url_for("static", filename=filename)


def admin_required(view_function):
    """Redirige a la pantalla de acceso si no hay una sesión administrativa."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if session.get("admin_authenticated") is not True:
            return redirect(url_for("admin_login"))
        return view_function(*args, **kwargs)

    return wrapped_view


@app.context_processor
def inject_globals():
    return {
        "format_currency": formatear_moneda,
        "product_image": product_image,
        "is_admin": session.get("admin_authenticated") is True,
        "total_productos": inventario.total_productos(),
        "productos": inventario.listar_productos(),
    }


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("error.html", error_title="Página no encontrada", message="El recurso que buscas no existe."), 404


@app.route("/")
def index():
    productos = inventario.listar_productos()
    return render_template("index.html", productos=productos, client_area=True)


@app.route("/clientes")
def clientes():
    """Muestra el catálogo de productos para los clientes."""
    productos = inventario.listar_productos()
    return render_template("index.html", productos=productos, client_area=True)


@app.route("/producto/<int:producto_id>")
def detalle(producto_id: int):
    try:
        producto = inventario.buscar_por_id(producto_id)
    except NotFoundError:
        return render_template("error.html", error_title="Producto no encontrado", message="No existe un producto con ese identificador."), 404

    return render_template("detalle.html", producto=producto)


@app.route("/comprar/<int:producto_id>", methods=["POST"])
def comprar_producto(producto_id: int):
    if session.get("admin_authenticated") is True:
        flash("El modo administrador no permite realizar compras.", "error")
        return redirect(url_for("admin"))

    try:
        nombre_cliente = validar_nombre(request.form.get("nombre_cliente", ""))
        correo = request.form.get("correo", "").strip()
        if "@" not in correo or "." not in correo.rsplit("@", 1)[-1]:
            raise ValidationError("Ingresa un correo electrónico válido.")

        cantidad_texto = request.form.get("cantidad", "")
        try:
            cantidad = int(cantidad_texto)
        except ValueError as exc:
            raise ValidationError("La cantidad debe ser un número entero.") from exc

        producto = inventario.buscar_por_id(producto_id)
        if producto.stock == 0:
            raise ValidationError("Este producto está agotado.")
        precio_unitario = producto.calcular_precio_final()
        producto = inventario.descontar_stock(producto_id, cantidad)
        try:
            venta = ventas.registrar(producto, cantidad, precio_unitario)
        except (OSError, ValueError):
            producto.stock += cantidad
            inventario.guardar_en_json()
            raise

        flash(
            f"Gracias, {nombre_cliente}. Compra #{venta['id']} confirmada. "
            f"Total: {formatear_moneda(venta['total'])}. No se procesó ningún pago.",
            "success",
        )
        return redirect(url_for("detalle", producto_id=producto_id))
    except (NotFoundError, ValidationError, OSError, ValueError) as exc:
        try:
            producto = inventario.buscar_por_id(producto_id)
        except NotFoundError:
            return render_template(
                "error.html",
                error_title="Producto no encontrado",
                message="No existe un producto con ese identificador.",
            ), 404
        return render_template("detalle.html", producto=producto, purchase_error=str(exc)), 400


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_authenticated") is True:
        return redirect(url_for("admin"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        valid_username = hmac.compare_digest(username, ADMIN_USERNAME)
        valid_password = hmac.compare_digest(password, ADMIN_PASSWORD)

        if valid_username and valid_password:
            session.clear()
            session["admin_authenticated"] = True
            return redirect(url_for("admin"))
        error = "Usuario o contraseña incorrectos. Inténtalo nuevamente."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("clientes"))


@app.route("/admin")
@admin_required
def admin():
    stats = inventario.obtener_estadisticas()
    return render_template(
        "administrador.html",
        stats=stats,
        productos=inventario.listar_productos(),
        ventas=ventas.listar(),
    )


@app.route("/admin/productos", methods=["POST"])
@admin_required
def registrar_producto():
    try:
        tipo = request.form.get("tipo", "").strip().lower()
        nombre = request.form.get("nombre", "").strip()
        precio_base = request.form.get("precio_base", "").strip()
        stock = request.form.get("stock", "").strip()

        if tipo in {"electrónico", "electronico"}:
            garantia = request.form.get("garantia_meses", "").strip()
            producto = Electronico(
                nombre=nombre,
                precio_base=float(precio_base),
                stock=int(stock),
                garantia_meses=int(garantia),
            )
        elif tipo == "libro":
            autor = request.form.get("autor", "").strip()
            texto = request.form.get("es_libro_texto", "").strip().lower() == "1"
            producto = Libro(
                nombre=nombre,
                precio_base=float(precio_base),
                stock=int(stock),
                autor=autor,
                es_libro_texto=texto,
            )
        else:
            raise ValidationError("El tipo de producto debe ser 'electrónico' o 'libro'.")

        inventario.agregar_producto(producto)
        return redirect(url_for("admin"))
    except ValueError as exc:
        raise ValidationError("Verifique que los valores numéricos estén escritos correctamente.") from exc
    except ValidationError as exc:
        return render_template(
            "administrador.html",
            error=str(exc),
            stats=inventario.obtener_estadisticas(),
            productos=inventario.listar_productos(),
            ventas=ventas.listar(),
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
