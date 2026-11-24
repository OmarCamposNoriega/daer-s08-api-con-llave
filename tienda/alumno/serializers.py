"""PARTE 1 — El contrato de datos: qué entra y qué sale por la API.

Un serializer decide tres cosas: qué campos se muestran, cuáles se pueden escribir y qué datos se rechazan.
Las pruebas de tienda/tests/test_p1_contrato.py dicen exactamente qué se espera. Comprueben con:

    python manage.py duelo

CategoriaSerializer ya está hecho, como ejemplo.
"""

from rest_framework import serializers

from tienda.models import Categoria, LineaPedido, Pedido, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class ProductoSerializer(serializers.ModelSerializer):
    # TODO 1. Un campo de solo lectura `categoria_nombre` con el nombre de la categoría
    #         (pista: CharField con source='categoria.nombre' y read_only=True).

    class Meta:
        model = Producto
        # TODO 2. La lista EXPLÍCITA de campos públicos:
        #         id, nombre, categoria, categoria_nombre, precio, stock, descripcion.
        #         `costo` es interno: no puede salir por la API. ¿Por qué no sirve '__all__'?
        fields = ['id', 'nombre']

    # TODO 3. validate_nombre: rechazar un nombre que ya exista SIN distinguir mayúsculas
    #         («FANTA 500ML» ya existe). Al editar, el propio producto no cuenta como repetido.
    # TODO 4. validate_precio: el precio tiene que ser mayor que cero.
    # TODO 5. validate_stock: el stock no puede ser negativo.
    # Cada validate_<campo>(self, valor) devuelve el valor o lanza serializers.ValidationError('mensaje').


class LineaPedidoSerializer(serializers.ModelSerializer):
    # TODO 6. `producto` como el NOMBRE del producto (solo lectura) y `subtotal` = cantidad × precio_unitario,
    #         como texto con dos decimales (pista: SerializerMethodField y f'{valor:.2f}').

    class Meta:
        model = LineaPedido
        fields = ['cantidad', 'precio_unitario']


class PedidoSerializer(serializers.ModelSerializer):
    # TODO 7. `cliente` como el nombre del cliente, `lineas` con LineaPedidoSerializer(many=True, read_only=True)
    #         y `total` = suma de los subtotales, como texto con dos decimales. Todo de solo lectura.

    class Meta:
        model = Pedido
        fields = ['id', 'fecha', 'estado']
