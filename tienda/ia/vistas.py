# Escrito por un asistente de IA a partir de este pedido:
#   «Ahora las vistas con vistas genéricas. El catálogo lo puede ver cualquiera; los pedidos, solo usuarios
#    con cuenta; anular un pedido, solo el personal de la tienda. Filtros ?categoria= y ?q= en productos.»
# Su respuesta: «¡Hecho! Usé los permisos estándar de DRF, así no reinventamos la rueda.»
#
# NO editen este archivo: para la Parte 4 cópienlo con `python manage.py duelo --iniciar-corregida`.

from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda.models import Categoria, Pedido, Producto

from .serializers import CategoriaSerializer, PedidoSerializer, ProductoSerializer


class EsPersonalOSoloLectura(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_staff


class CategoriaLista(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsPersonalOSoloLectura]


class CategoriaDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsPersonalOSoloLectura]


class ProductoLista(generics.ListCreateAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria')
        if categoria := self.request.query_params.get('categoria'):
            qs = qs.filter(categoria__nombre__iexact=categoria)
        if q := self.request.query_params.get('q'):
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        return qs


class ProductoDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.select_related('categoria')
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PedidoLista(generics.ListAPIView):
    queryset = Pedido.objects.select_related('cliente').prefetch_related('lineas__producto')
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


class PedidoDetalle(generics.RetrieveAPIView):
    queryset = Pedido.objects.select_related('cliente').prefetch_related('lineas__producto')
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnularPedido(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        pedido = Pedido.objects.get(pk=pk)
        if pedido.estado == Pedido.ANULADO:
            return Response({'detail': 'El pedido ya estaba anulado.'}, status=status.HTTP_409_CONFLICT)
        pedido.estado = Pedido.ANULADO
        pedido.save(update_fields=['estado'])
        return Response(PedidoSerializer(pedido).data)
