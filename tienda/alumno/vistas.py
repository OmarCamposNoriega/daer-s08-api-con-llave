"""PARTES 2 y 3 - Vistas genericas de la API y control de permisos por rol."""

from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda.models import Categoria, Pedido, Producto

from .serializers import CategoriaSerializer, PedidoSerializer, ProductoSerializer


class PorHacer(APIView):
    """Responde 501 mientras se completa la vista correspondiente."""

    def por_hacer(self, request, *args, **kwargs):
        return Response({'detail': f'{type(self).__name__} esta por hacer.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    get = post = put = patch = delete = por_hacer


class CategoriaLista(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class CategoriaDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ProductoLista(generics.ListCreateAPIView):
    serializer_class = ProductoSerializer

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria')
        categoria = self.request.query_params.get('categoria')
        if categoria:
            qs = qs.filter(categoria__nombre__iexact=categoria)
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        return qs


class ProductoDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.select_related('categoria')
    serializer_class = ProductoSerializer


class PedidoLista(generics.ListAPIView):
    queryset = Pedido.objects.select_related('cliente').prefetch_related('lineas__producto')
    serializer_class = PedidoSerializer


class PedidoDetalle(generics.RetrieveAPIView):
    queryset = Pedido.objects.select_related('cliente').prefetch_related('lineas__producto')
    serializer_class = PedidoSerializer


class AnularPedido(PorHacer):
    pass


_ = permissions
