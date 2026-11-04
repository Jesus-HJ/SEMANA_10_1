# TechBook Store

TechBook Store es una aplicación desarrollada con Python y Flask para gestionar un catálogo de productos electrónicos y libros. El proyecto integra una interfaz CLI y una web moderna con una arquitectura orientada a objetos, validaciones, manejo de errores y persistencia JSON.

## 1. Descripción general

La práctica se enmarca en la Semana 10 del curso de Desarrollo de Aplicaciones Web. El objetivo es demostrar:

- Programación orientada a objetos.
- Herencia, encapsulamiento y polimorfismo.
- Validaciones robustas.
- Excepciones personalizadas.
- Estructuras condicionales y ciclos.
- Modularización con paquetes Python.
- Interfaz CLI y Flask.

## 2. Tecnologías

- Python 3.11+
- Flask
- HTML5, CSS3 y JavaScript vanilla
- Jinja2
- unittest

## 3. Requisitos previos

- Python 3.11 o superior.
- pip actualizado.

## 4. Instalación

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-web.txt

## 5. Estructura del proyecto

techbook-store/
├── main.py
├── app.py
├── requirements.txt
├── requirements-web.txt
├── README.md
├── .gitignore
├── models/
│   ├── __init__.py
│   ├── inventario.py
│   ├── mixins.py
│   ├── producto.py
│   └── ventas.py
├── utils/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── formatters.py
│   └── validators.py
├── templates/
│   ├── administrador.html
│   ├── base.html
│   ├── detalle.html
│   ├── error.html
│   └── index.html
├── static/
│   ├── css/
│   └── js/
├── data/
│   ├── productos.json
│   └── ventas.json (se crea al registrar la primera compra)
├── tests/
│   ├── test_inventario.py
│   ├── test_producto.py
│   ├── test_validators.py
│   └── test_web.py
└── docs/

## 6. Clases principales

### Producto

Es la clase base con atributos comunes: ID, nombre, precio base, stock y categoría.

### Electronico

Hereda de `Producto` y agrega garantía y lógica para IGV y descuento por stock mayor a 50 unidades.

### Libro

Hereda de `Producto` y agrega autor e indicador de libro de texto.

### Inventario

Gestiona el catálogo, la búsqueda, el agregado y la persistencia JSON.

## 7. Herencia, encapsulamiento y polimorfismo

El sistema usa herencia para reutilizar la lógica base. El encapsulamiento se aplica con propiedades `@property` y setters que validan datos. El polimorfismo está presente en `calcular_precio_final()`, que se comporta de forma distinta según el tipo de producto.

producto = libro_o_electronico
precio = producto.calcular_precio_final()

## 8. MRO y super()

Python resuelve el orden de métodos usando Method Resolution Order (MRO). En la práctica, se puede verificar con:

print(Electronico.__mro__)
print(Libro.__mro__)

La clase `Electronico` usa `super().__init__()` para inicializar los atributos de `Producto`, y la misma lógica aplica a `Libro`.

## 9. Excepciones

Se utilizan `ValidationError` y `NotFoundError` para manejar errores amigables y evitar cierres inesperados.

## 10. CLI

Ejecuta la aplicación de consola:

python main.py

El menú ofrece:

1. Agregar producto
2. Listar productos
3. Calcular precio final
4. Salir

## 11. Web

Inicia la aplicación Flask:

python app.py

Luego abre:

http://localhost:5000/

Las áreas están separadas por ruta:

- **Clientes:** `http://localhost:5000/clientes` para explorar y filtrar el catálogo.
- **Administrador:** `http://localhost:5000/admin/login` para iniciar sesión y, luego, registrar productos y consultar el inventario en `http://localhost:5000/admin`.

El catálogo de clientes es público. Para la demostración académica, las credenciales de administrador son `admin` / `admin`; el panel incluye la opción para cerrar sesión. Estas credenciales son fijas y no deben utilizarse en una publicación real. Antes de desplegar fuera de una red local, se deben reemplazar por autenticación y almacenamiento seguro de credenciales, así como configurar `TECHBOOK_SECRET_KEY` con un valor secreto propio.

La página inicial (`/`) abre directamente el área de clientes. Desde el menú superior se puede entrar al modo administrador. En el área de clientes, cada producto disponible tiene un formulario de compra que solicita nombre, correo y cantidad; no se realiza un pago ni se guarda la información de contacto. La compra descuenta el stock y el panel protegido muestra el stock actualizado y el historial de ventas, persistido en `data/ventas.json`.

La portada usa una composición editorial responsive y fotografías de producto guardadas localmente en `static/images`, así que no depende de un servidor de imágenes externo al ejecutarse. Las fotografías se obtuvieron de [Unsplash](https://unsplash.com/license) y se usan bajo su licencia:

- [Laptop](https://images.unsplash.com/photo-1496181133206-80ce9b88a853)
- [Monitor](https://images.unsplash.com/photo-1527443224154-c4a3942d3acf)
- [Audífonos](https://images.unsplash.com/photo-1505740420928-5e560c06d30e)
- [Teclado](https://images.unsplash.com/photo-1587829741301-dc798b83add3)
- [Libros apilados](https://images.unsplash.com/photo-1532012197267-da84d127e765) y [libro abierto](https://images.unsplash.com/photo-1512820790803-83ca734da794)

## 12. Pruebas automatizadas

python -m unittest discover -s tests -v

## 13. Justificación técnica

El proyecto mantiene la lógica de negocio separada de la capa web, aceptando los mismos objetos por ambos canales y aplicando las mismas reglas. Esto hace que la CLI y la interfaz web compartan la definición de producto y el inventario.

## 14. Limitaciones conocidas

- El sistema usa JSON local como almacenamiento sencillo.
- No incluye pagos reales ni autenticación.
- La aplicación web no reemplaza la CLI, sino que la complementa.

## 15. Mejoras adicionales

- Ordenación y filtros adicionales.
- Gestión de categorías más extensas.
- Persistencia en base de datos.
- Panel de edición y eliminación avanzada.

## 16. Diagrama UML

classDiagram
    class Producto {
        - _id: int
        - _nombre: str
        - _precio_base: float
        - _stock: int
        - _categoria: str
        + calcular_precio_final() float
        + __str__() str
    }
    class DescuentoMixin {
        + aplicar_descuento(precio, porcentaje) float
    }
    class Electronico {
        - _garantia_meses: int
        + calcular_precio_final() float
    }
    class Libro {
        - _autor: str
        - _es_libro_texto: bool
        + calcular_precio_final() float
    }
    class Inventario {
        - _productos: dict
        + agregar_producto(producto)
        + buscar_por_id(id)
        + listar_productos()
    }
    Producto <|-- Electronico
    Producto <|-- Libro
    DescuentoMixin <|-- Electronico
    DescuentoMixin <|-- Libro
    Inventario --> Producto

    ##17 Modo Administrador
    Usuario: admin
    Contraseña: admin