from django.contrib import admin

from .models import Categoria, Cliente, LineaPedido, Pedido, Producto

admin.site.register([Categoria, Producto, Cliente, Pedido, LineaPedido])
