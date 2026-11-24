"""PARTES 2 y 3 — Las vistas (qué rutas responden y cómo) y sus permisos (quién puede hacer qué).

Usen las vistas genéricas de DRF (generics.ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView,
RetrieveAPIView): con queryset y serializer_class ya dan GET, POST, PUT, PATCH y DELETE con los códigos
correctos (201 al crear, 204 al borrar, 404 si no existe, 400 si el serializer rechaza los datos).

Las rutas ya están en extra08/urls.py; aquí solo se escriben las clases. Las vistas de categoría ya están
hechas, como ejemplo, salvo sus permisos. Comprueben con:

    python manage.py duelo
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda.models import Categoria

from .serializers import CategoriaSerializer


class PorHacer(APIView):
    """Responde 501 («no implementado») a todo. Reemplácenla por la vista de verdad."""

    def por_hacer(self, request, *args, **kwargs):
        return Response({'detail': f'{type(self).__name__} está por hacer.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    get = post = put = patch = delete = por_hacer


# TODO P3-1. Un permiso propio, SoloPersonalEscribe (subclase de permissions.BasePermission):
#            cualquiera puede leer (métodos SAFE_METHODS: GET, HEAD, OPTIONS); crear, cambiar o borrar,
#            solo el personal de la tienda (request.user.is_staff). Úsenlo en categorías y productos.


class CategoriaLista(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # TODO P3-2. permission_classes


class CategoriaDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # TODO P3-2. permission_classes


class ProductoLista(PorHacer):
    """TODO P2-1. ListCreateAPIView de productos, con:
    - select_related('categoria'), para que la lista sea UNA consulta aunque muestre categoria_nombre;
    - ?categoria=<nombre> sin distinguir mayúsculas;
    - ?q=<texto> en el nombre O en la descripción (objetos Q, como en la S07).
    Pista: sobrescriban get_queryset(self) y lean self.request.query_params.get('categoria').
    TODO P3-2. Sus permission_classes.
    """


class ProductoDetalle(PorHacer):
    """TODO P2-2. RetrieveUpdateDestroyAPIView de un producto. TODO P3-2. Sus permission_classes."""


class PedidoLista(PorHacer):
    """TODO P2-3. ListAPIView de pedidos con sus líneas, sin N+1 (select_related + prefetch_related).
    TODO P3-3. Solo con credenciales: los pedidos traen datos de clientes."""


class PedidoDetalle(PorHacer):
    """TODO P2-4. RetrieveAPIView de un pedido. TODO P3-3. Solo con credenciales."""


class AnularPedido(PorHacer):
    """TODO P3-4. APIView con un método post(self, request, pk) que:
    - responde 404 si el pedido no existe (pista: get_object_or_404, no Pedido.objects.get);
    - responde 409 si ya estaba anulado;
    - si no, lo pasa a anulado y devuelve el pedido con PedidoSerializer.
    Solo el personal de la tienda puede anular (permissions.IsAdminUser).
    """


# Para no dejar imports sin usar mientras completan: bórrenlo cuando ya usen `permissions`.
_ = permissions
