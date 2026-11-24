# Escrito por un asistente de IA a partir de este pedido:
#   «Hazme los serializers de DRF para la tienda (categorías, productos y pedidos con sus líneas).
#    Que no se puedan registrar productos repetidos ni con stock negativo.»
# Su respuesta: «¡Listo! Usé ModelSerializer para aprovechar las validaciones del modelo y no repetir código.»
#
# NO editen este archivo: para la Parte 4 cópienlo con `python manage.py duelo --iniciar-corregida`.

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

    def validate_nombre(self, value):
        qs = Producto.objects.filter(nombre__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Ya existe un producto con ese nombre.')
        return value

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor que cero.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('El stock no puede ser negativo.')
        return value


class LineaPedidoSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='producto.nombre', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = LineaPedido
        fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']

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
        return f'{sum(l.cantidad * l.precio_unitario for l in obj.lineas.all()):.2f}'
