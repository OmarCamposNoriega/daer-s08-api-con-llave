"""PARTES 2 y 3 - Vistas genericas de la API y control de permisos por rol."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda.models import Categoria, Pedido, Producto

from .serializers import CategoriaSerializer, PedidoSerializer, ProductoSerializer


class SoloPersonalEscribe(permissions.BasePermission):
    """Permite lectura a cualquier cliente y restringe escritura al personal (is_staff)."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CategoriaLista(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [SoloPersonalEscribe]


class CategoriaDetalle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [SoloPersonalEscribe]


class ProductoLista(generics.ListCreateAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [SoloPersonalEscribe]

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
    permission_classes = [SoloPersonalEscribe]


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
        pedido = get_object_or_404(
            Pedido.objects.select_related('cliente').prefetch_related('lineas__producto'),
            pk=pk,
        )
        if pedido.estado == Pedido.ANULADO:
            return Response(
                {'detail': 'El pedido ya estaba anulado.'},
                status=status.HTTP_409_CONFLICT,
            )
        pedido.estado = Pedido.ANULADO
        pedido.save(update_fields=['estado'])
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)
