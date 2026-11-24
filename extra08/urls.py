"""Rutas de la API. Ya están completas: no hace falta tocarlas.

Las vistas salen de la versión activa (alumno, ia, corregida o solucion; ver tienda/version.py), así que la
misma ruta sirve el código de cada versión.

    /api/categorias/              GET lista · POST crea
    /api/categorias/<id>/         GET · PUT · PATCH · DELETE
    /api/productos/               GET lista (?categoria=<nombre>  ?q=<texto>) · POST crea
    /api/productos/<id>/          GET · PUT · PATCH · DELETE
    /api/pedidos/                 GET lista (solo con credenciales)
    /api/pedidos/<id>/            GET detalle con líneas y total (solo con credenciales)
    /api/pedidos/<id>/anular/     POST anula el pedido (solo el personal de la tienda)
    /api/token/                   POST usuario y clave → su token
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from tienda.version import modulo

v = modulo('vistas')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/categorias/', v.CategoriaLista.as_view(), name='categoria-lista'),
    path('api/categorias/<int:pk>/', v.CategoriaDetalle.as_view(), name='categoria-detalle'),
    path('api/productos/', v.ProductoLista.as_view(), name='producto-lista'),
    path('api/productos/<int:pk>/', v.ProductoDetalle.as_view(), name='producto-detalle'),
    path('api/pedidos/', v.PedidoLista.as_view(), name='pedido-lista'),
    path('api/pedidos/<int:pk>/', v.PedidoDetalle.as_view(), name='pedido-detalle'),
    path('api/pedidos/<int:pk>/anular/', v.AnularPedido.as_view(), name='pedido-anular'),
    path('api/token/', obtain_auth_token, name='token'),
    path('api-auth/', include('rest_framework.urls')),  # «Log in» de la API navegable
]
