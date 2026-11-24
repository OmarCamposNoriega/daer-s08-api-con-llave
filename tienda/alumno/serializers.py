"""PARTE 1 - Contrato de datos (serializers) para categorias, productos y pedidos."""

from decimal import Decimal

from rest_framework import serializers

from tienda.models import Categoria, LineaPedido, Pedido, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'categoria', 'categoria_nombre', 'precio', 'stock', 'descripcion']

    def validate_nombre(self, valor):
        qs = Producto.objects.filter(nombre__iexact=valor)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un producto con ese nombre.')
        return valor

    def validate_precio(self, valor):
        if valor <= 0:
            raise serializers.ValidationError('El precio debe ser mayor que cero.')
        return valor

    def validate_stock(self, valor):
        if valor < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return valor


class LineaPedidoSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = LineaPedido
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = fields

    def get_subtotal(self, obj):
        return f'{obj.cantidad * obj.precio_unitario:.2f}'


class PedidoSerializer(serializers.ModelSerializer):
    cliente = serializers.CharField(source='cliente.nombre', read_only=True)
    lineas = LineaPedidoSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'fecha', 'estado', 'lineas', 'total']
        read_only_fields = fields

    def get_total(self, obj):
        suma = sum((linea.cantidad * linea.precio_unitario for linea in obj.lineas.all()), Decimal('0.00'))
        return f'{suma:.2f}'
