"""Parte 1 — El contrato de datos (serializers). NO editen las pruebas: son el oráculo del laboratorio."""

from tienda.models import Producto

from .base import PruebaAPI


class ContratoTests(PruebaAPI):
    def test_producto_expone_solo_campos_publicos(self):
        datos = self.anonimo.get('/api/productos/1/').json()
        self.assertEqual(set(datos), {'id', 'nombre', 'categoria', 'categoria_nombre', 'precio', 'stock', 'descripcion'},
                         'el producto tiene que mostrar exactamente los campos públicos (y nunca el costo)')
        self.assertEqual((datos['nombre'], datos['categoria_nombre'], datos['precio']), ('Fanta 500ml', 'Gaseosas', '1.80'))

    def test_precio_debe_ser_mayor_que_cero(self):
        for precio in ('0', '-1.50'):
            r = self.admin.post('/api/productos/', self.nuevo_producto(precio=precio), format='json')
            self.assertEqual(r.status_code, 400, f'precio {precio}: se aceptó')
            self.assertIn('precio', r.json())
        self.assertFalse(Producto.objects.filter(nombre='Sublime Blanco').exists())

    def test_stock_no_puede_ser_negativo(self):
        r = self.admin.post('/api/productos/', self.nuevo_producto(stock=-3), format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('stock', r.json())

    def test_nombre_repetido_sin_distinguir_mayusculas(self):
        r = self.admin.post('/api/productos/', self.nuevo_producto(nombre='FANTA 500ML'), format='json')
        self.assertEqual(r.status_code, 400, '«FANTA 500ML» es el mismo producto que «Fanta 500ml»')
        self.assertIn('nombre', r.json())
        # Editar un producto sin cambiarle el nombre no es «repetirlo».
        r = self.admin.patch('/api/productos/1/', {'nombre': 'Fanta 500ml', 'stock': 11}, format='json')
        self.assertEqual(r.status_code, 200)

    def test_categoria_nombre_es_solo_lectura(self):
        r = self.admin.post('/api/productos/', self.nuevo_producto(categoria_nombre='Inventada'), format='json')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['categoria_nombre'], 'Chocolates')

    def test_pedido_con_lineas_y_total(self):
        datos = self.agente.get('/api/pedidos/1/').json()
        self.assertEqual((datos['id'], datos['cliente'], datos['estado'], datos['total']), (1, 'Ana Quispe', 'pagado', '6.60'))
        self.assertEqual(datos['lineas'], [
            {'producto': 'Fanta 500ml', 'cantidad': 2, 'precio_unitario': '1.80', 'subtotal': '3.60'},
            {'producto': 'Picaras', 'cantidad': 3, 'precio_unitario': '1.00', 'subtotal': '3.00'}])
