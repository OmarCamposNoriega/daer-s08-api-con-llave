"""Ejecuta contra la API un plan de llamadas HTTP, como lo haría un agente de IA sin pantalla (headless).

    python manage.py ejecutar_plan planes/plan_del_agente.json --como agente
    python manage.py ejecutar_plan planes/plan_del_agente.json --como admin
    python manage.py ejecutar_plan planes/plan_del_agente.json --como anonimo --json
    python manage.py ejecutar_plan planes/plan_del_agente.json --como agente --aplicar

El plan es una lista JSON de pasos {"metodo", "ruta", "datos" (opcional), "motivo"}. Cada paso se manda a la API
con el token del usuario elegido, igual que si llegara por la red, y se anota el código que respondió.

Por defecto es un SIMULACRO: al terminar se deshacen todos los cambios. Con --aplicar se quedan.
La API decide qué pasos se cumplen; este comando no filtra nada.
"""

import json
import logging
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

USUARIOS = ('anonimo', 'agente', 'admin')


class Command(BaseCommand):
    help = 'Ejecuta un plan de llamadas a la API con el token de un usuario (simulacro por defecto).'

    def add_arguments(self, parser):
        parser.add_argument('plan', help='archivo JSON con la lista de pasos')
        parser.add_argument('--como', choices=USUARIOS, default='agente', help='con qué credenciales llamar')
        parser.add_argument('--aplicar', action='store_true', help='deja los cambios (sin esto, se deshacen)')
        parser.add_argument('--json', action='store_true', help='salida en JSON, para programas')

    def handle(self, *args, plan, como, aplicar, json: bool, **options):
        pasos = self.leer_plan(plan)
        # Django anota cada 4xx como aviso («Forbidden: …»); aquí ya se muestra el código de cada paso.
        logging.getLogger('django.request').setLevel(logging.ERROR)
        cliente = APIClient()
        if como != 'anonimo':
            token = Token.objects.filter(user__username=como).first()
            if token is None:
                raise CommandError(f'No hay token para «{como}». ¿Corrieron python manage.py cargar_datos?')
            cliente.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resultados = []
        with transaction.atomic():
            for numero, paso in enumerate(pasos, start=1):
                metodo = paso['metodo'].lower()
                respuesta = getattr(cliente, metodo)(paso['ruta'], paso.get('datos'), format='json')
                resultados.append({'paso': numero, 'metodo': paso['metodo'].upper(), 'ruta': paso['ruta'],
                                   'motivo': paso.get('motivo', ''), 'codigo': respuesta.status_code,
                                   'respuesta': self.resumen(respuesta)})
            if not aplicar:
                transaction.set_rollback(True)

        if json:
            self.stdout.write(_json_texto(resultados))
            return
        self.stdout.write(f'Plan: {plan} · como: {como} · {"SE APLICA" if aplicar else "simulacro (se deshace al final)"}\n')
        for r in resultados:
            estilo = self.style.SUCCESS if r['codigo'] < 300 else self.style.ERROR
            self.stdout.write(estilo(f'{r["paso"]}. {r["codigo"]} {r["metodo"]:6} {r["ruta"]}'))
            self.stdout.write(f'   motivo del agente: {r["motivo"]}')
            self.stdout.write(f'   respuesta: {r["respuesta"]}')
        cumplidos = sum(r['codigo'] < 300 for r in resultados)
        self.stdout.write(f'\n{cumplidos} de {len(resultados)} pasos cumplidos.')

    def leer_plan(self, plan):
        ruta = Path(plan)
        if not ruta.is_absolute() and not ruta.exists():
            ruta = Path(settings.BASE_DIR) / plan
        try:
            pasos = json.loads(ruta.read_text(encoding='utf-8'))
        except FileNotFoundError:
            raise CommandError(f'No existe el plan {plan}') from None
        except ValueError as e:
            raise CommandError(f'El plan {plan} no es JSON válido: {e}') from None
        if not isinstance(pasos, list) or not all(isinstance(p, dict) and 'metodo' in p and 'ruta' in p for p in pasos):
            raise CommandError('El plan tiene que ser una lista de pasos con "metodo" y "ruta".')
        return pasos

    def resumen(self, respuesta):
        try:
            datos = respuesta.json()
        except ValueError:
            return respuesta.content.decode('utf-8', 'replace')[:120]
        if isinstance(datos, list):
            return f'lista de {len(datos)}'
        texto = _json_texto(datos)
        return texto if len(texto) <= 160 else texto[:157] + '...'


def _json_texto(datos):
    return json.dumps(datos, ensure_ascii=False)
