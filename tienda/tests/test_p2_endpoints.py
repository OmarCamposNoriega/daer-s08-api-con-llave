"""Parte 2 — Los endpoints (vistas genéricas). NO editen las pruebas: son el oráculo del laboratorio."""

from .base import PruebaAPI

TODOS = ['7up 500ml', 'Cheetos', 'Chizito', 'Coca Cola 500ml', 'Coronita Fresa', 'Fanta 500ml', 'Picaras',
         'Princesa', 'Sublime', 'Triángulo']


class EndpointsTests(PruebaAPI):
    def nombres(self, ruta):
        r = self.anonimo.get(ruta)
        self.assertEqual(r.status_code, 200, ruta)
        return [p['nombre'] for p in r.json()]

    def test_lista_de_productos(self):
        self.assertEqual(self.nombres('/api/productos/'), TODOS)

    def test_lista_de_productos_en_una_consulta(self):
        with self.assertNumQueries(1):
            self.anonimo.get('/api/productos/')

    def test_filtrar_por_categoria_sin_distinguir_mayusculas(self):
        for nombre in ('Gaseosas', 'GASEOSAS'):
            self.assertEqual(self.nombres(f'/api/productos/?categoria={nombre}'),
                             ['7up 500ml', 'Coca Cola 500ml', 'Fanta 500ml'], nombre)
        self.assertEqual(self.nombres('/api/productos/?categoria=Helados'), [])

    def test_buscar_en_nombre_o_descripcion(self):
        self.assertEqual(self.nombres('/api/productos/?q=chocolate'), ['Picaras', 'Princesa', 'Sublime', 'Triángulo'])
        self.assertEqual(self.nombres('/api/productos/?q=FANTA'), ['Fanta 500ml'])

    def test_crear_cambiar_y_borrar_un_producto(self):
        r = self.admin.post('/api/productos/', self.nuevo_producto(), format='json')
        self.assertEqual(r.status_code, 201)
        nuevo = r.json()['id']
        r = self.admin.patch(f'/api/productos/{nuevo}/', {'stock': 9}, format='json')
        self.assertEqual((r.status_code, r.json()['stock']), (200, 9))
        self.assertEqual(self.admin.delete(f'/api/productos/{nuevo}/').status_code, 204)
        self.assertEqual(self.anonimo.get(f'/api/productos/{nuevo}/').status_code, 404)

    def test_producto_inexistente_da_404(self):
        self.assertEqual(self.anonimo.get('/api/productos/999/').status_code, 404)
