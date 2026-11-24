"""Parte 3 — Quién puede hacer qué (autenticación y permisos). NO editen las pruebas: son el oráculo."""

import json
from io import StringIO

from django.core.management import call_command

from tienda.models import Pedido, Producto

from .base import TOKENS, PruebaAPI


class PermisosTests(PruebaAPI):
    def test_anonimo_lee_el_catalogo_pero_no_lo_cambia(self):
        self.assertEqual(self.anonimo.get('/api/productos/').status_code, 200)
        self.assertEqual(self.anonimo.get('/api/categorias/').status_code, 200)
        self.assertEqual(self.anonimo.post('/api/productos/', self.nuevo_producto(), format='json').status_code, 401)
        self.assertEqual(self.anonimo.post('/api/categorias/', {'nombre': 'Helados'}, format='json').status_code, 401)

    def test_el_agente_no_cambia_el_catalogo(self):
        r = self.agente.post('/api/productos/', self.nuevo_producto(), format='json')
        self.assertEqual(r.status_code, 403, 'el agente pudo CREAR un producto')
        r = self.agente.patch('/api/productos/3/', {'stock': 24}, format='json')
        self.assertEqual(r.status_code, 403, 'el agente pudo CAMBIAR el stock')
        self.assertEqual(self.agente.delete('/api/categorias/4/').status_code, 403)
        self.assertEqual(Producto.objects.get(pk=3).stock, 0)

    def test_el_admin_si_cambia_el_catalogo(self):
        self.assertEqual(self.admin.post('/api/productos/', self.nuevo_producto(), format='json').status_code, 201)
        self.assertEqual(self.admin.post('/api/categorias/', {'nombre': 'Helados'}, format='json').status_code, 201)

    def test_los_pedidos_piden_credenciales(self):
        self.assertEqual(self.anonimo.get('/api/pedidos/').status_code, 401)
        self.assertEqual(self.anonimo.get('/api/pedidos/1/').status_code, 401)
        r = self.agente.get('/api/pedidos/')
        self.assertEqual((r.status_code, len(r.json())), (200, 7))

    def test_solo_el_personal_anula_un_pedido(self):
        self.assertEqual(self.agente.post('/api/pedidos/6/anular/').status_code, 403)
        self.assertEqual(Pedido.objects.get(pk=6).estado, 'pendiente')
        r = self.admin.post('/api/pedidos/6/anular/')
        self.assertEqual((r.status_code, r.json()['estado']), (200, 'anulado'))
        self.assertEqual(self.admin.post('/api/pedidos/6/anular/').status_code, 409, 'anular dos veces')

    def test_anular_un_pedido_inexistente_da_404(self):
        self.assertEqual(self.admin.post('/api/pedidos/999/anular/').status_code, 404)

    def test_token_con_usuario_y_clave(self):
        r = self.anonimo.post('/api/token/', {'username': 'agente', 'password': 'agente12345'}, format='json')
        self.assertEqual((r.status_code, r.json().get('token')), (200, TOKENS['agente']))

    def test_el_plan_en_simulacro_no_cambia_nada(self):
        salida = StringIO()
        call_command('ejecutar_plan', 'planes/plan_del_agente.json', '--como', 'admin', '--json', stdout=salida)
        pasos = json.loads(salida.getvalue())
        self.assertEqual(len(pasos), 6)
        self.assertTrue(all('codigo' in p for p in pasos))
        self.assertEqual(Pedido.objects.get(pk=6).estado, 'pendiente', 'el simulacro dejó el pedido anulado')
        self.assertEqual(Producto.objects.get(pk=3).stock, 0, 'el simulacro dejó el stock cambiado')
