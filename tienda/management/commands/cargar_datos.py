"""Carga la tienda con datos FIJOS: siempre los mismos, para que cada llamada a la API tenga una respuesta conocida.

4 categorías, 10 productos, 4 clientes, 7 pedidos (5 pagados, 1 pendiente, 1 anulado) y dos usuarios con su token:

    admin    personal de la tienda (is_staff): puede cambiar el catálogo y anular pedidos
    agente   la cuenta del asistente de IA: puede leer, pero no cambiar nada

Las claves y los tokens son de laboratorio y están escritos aquí a propósito: en un sistema real, nunca.
Se puede repetir: borra todo y lo vuelve a crear igual.
"""

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

from tienda.models import Categoria, Cliente, LineaPedido, Pedido, Producto

LIMA = ZoneInfo('America/Lima')

# (categoría, nombre, precio, stock, descripción, costo)
PRODUCTOS = [
    ('Gaseosas', 'Fanta 500ml', '1.80', 10, 'Gaseosa de naranja.', '1.10'),
    ('Gaseosas', 'Coca Cola 500ml', '2.50', 4, 'Gaseosa cola clásica.', '1.60'),
    ('Gaseosas', '7up 500ml', '1.70', 0, 'Lima-limón, sin cafeína.', '1.05'),
    ('Galletas', 'Picaras', '1.00', 12, 'Galleta con relleno de chocolate.', '0.55'),
    ('Galletas', 'Coronita Fresa', '0.70', 3, 'Galleta con crema de fresa.', '0.40'),
    ('Snacks', 'Cheetos', '1.00', 12, 'Snack de maíz con queso.', '0.60'),
    ('Snacks', 'Chizito', '1.00', 2, 'Snack de maíz, el de siempre.', '0.58'),
    ('Chocolates', 'Sublime', '1.50', 8, 'Chocolate con maní.', '0.90'),
    ('Chocolates', 'Princesa', '1.50', 6, 'Chocolate con galleta.', '0.85'),
    ('Chocolates', 'Triángulo', '1.20', 1, 'Chocolate relleno de maní.', '0.70'),
]
CLIENTES = [('Ana Quispe', 'ana@example.com', 'Lima'), ('Luis Torres', 'luis@example.com', 'Arequipa'),
            ('María Rojas', 'maria@example.com', 'Lima'), ('Pedro Vega', 'pedro@example.com', 'Cusco')]
# (cliente, día de octubre de 2026, estado, [(producto, cantidad)])
PEDIDOS = [
    ('Ana Quispe', 3, 'pagado', [('Fanta 500ml', 2), ('Picaras', 3)]),
    ('Ana Quispe', 10, 'pagado', [('Sublime', 4)]),
    ('Luis Torres', 12, 'pagado', [('Coca Cola 500ml', 1), ('Cheetos', 2)]),
    ('Luis Torres', 15, 'anulado', [('Princesa', 10)]),
    ('María Rojas', 20, 'pagado', [('Triángulo', 2), ('Fanta 500ml', 1)]),
    ('Ana Quispe', 25, 'pendiente', [('Chizito', 1)]),
    ('Luis Torres', 28, 'pagado', [('Picaras', 1)]),
]
# (usuario, clave, es personal, token). De laboratorio: así la guía puede nombrarlos.
USUARIOS = [
    ('admin', 'admin12345', True, 'admin-token-de-laboratorio-0000000000001'),
    ('agente', 'agente12345', False, 'agente-token-de-laboratorio-00000000002'),
]


class Command(BaseCommand):
    help = 'Carga la tienda y los usuarios admin y agente con datos fijos (se puede repetir).'

    @transaction.atomic
    def handle(self, *args, **options):
        LineaPedido.objects.all().delete()
        Pedido.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        Cliente.objects.all().delete()
        User.objects.filter(username__in=[u for u, *_ in USUARIOS]).delete()

        # Ids fijos: SQLite no reutiliza los ids borrados y la guía nombra categorías, productos y pedidos por número.
        categorias = {}
        for numero, nombre in enumerate(sorted({p[0] for p in PRODUCTOS}), start=1):
            categorias[nombre] = Categoria.objects.create(pk=numero, nombre=nombre)
        productos = {}
        for numero, (cat, nombre, precio, stock, descripcion, costo) in enumerate(PRODUCTOS, start=1):
            productos[nombre] = Producto.objects.create(
                pk=numero, categoria=categorias[cat], nombre=nombre, precio=Decimal(precio), stock=stock,
                descripcion=descripcion, costo=Decimal(costo))
        clientes = {n: Cliente.objects.create(pk=i, nombre=n, email=e, ciudad=c)
                    for i, (n, e, c) in enumerate(CLIENTES, start=1)}
        for numero, (cliente, dia, estado, lineas) in enumerate(PEDIDOS, start=1):
            pedido = Pedido.objects.create(pk=numero, cliente=clientes[cliente], estado=estado,
                                           fecha=datetime(2026, 10, dia, 11, 0, tzinfo=LIMA))
            for producto, cantidad in lineas:
                LineaPedido.objects.create(pedido=pedido, producto=productos[producto], cantidad=cantidad,
                                           precio_unitario=productos[producto].precio)
        for usuario, clave, personal, token in USUARIOS:
            u = User.objects.create_user(usuario, password=clave, is_staff=personal, is_superuser=personal)
            Token.objects.create(user=u, key=token)

        self.stdout.write(self.style.SUCCESS(
            f'{Categoria.objects.count()} categorías, {Producto.objects.count()} productos, '
            f'{Cliente.objects.count()} clientes, {Pedido.objects.count()} pedidos '
            f'y los usuarios {" y ".join(u for u, *_ in USUARIOS)}.'))
