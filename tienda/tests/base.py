"""Base común de las pruebas: datos fijos y tres clientes HTTP (anónimo, agente y admin). NO se edita."""

from io import StringIO

from django.core.management import call_command
from rest_framework.test import APIClient, APITestCase

from tienda.management.commands.cargar_datos import USUARIOS

TOKENS = {usuario: token for usuario, _clave, _personal, token in USUARIOS}


class PruebaAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', stdout=StringIO())

    def setUp(self):
        self.anonimo = APIClient()
        self.agente = APIClient()
        self.agente.credentials(HTTP_AUTHORIZATION=f'Token {TOKENS["agente"]}')
        self.admin = APIClient()
        self.admin.credentials(HTTP_AUTHORIZATION=f'Token {TOKENS["admin"]}')

    def nuevo_producto(self, **cambios):
        datos = {'nombre': 'Sublime Blanco', 'categoria': 1, 'precio': '1.80', 'stock': 5,
                 'descripcion': 'Chocolate blanco con maní.'}
        return {**datos, **cambios}
