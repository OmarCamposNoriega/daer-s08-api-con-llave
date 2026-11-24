# Lab extra S08 — La API con llave: Django REST Framework, tokens y lo que un agente puede hacer

En la S07 la tienda tuvo consumidores sin pantalla que **solo leían**. Esta semana la tienda tiene una **API REST**
de verdad, y por una API también se **escribe**: crear productos, cambiar el stock, anular pedidos. Si un agente de
IA usa la API, lo que puede hacer no lo decide el agente: lo deciden **el serializer** (qué datos se aceptan) y **los
permisos** (quién puede hacer qué).

1. **Parte 1:** el contrato de datos. Serializers con campos explícitos y validaciones (`tienda/alumno/serializers.py`).
2. **Parte 2:** los endpoints. Vistas genéricas con filtros y sin consultas de más (`tienda/alumno/vistas.py`), y un
   cliente en PowerShell.
3. **Parte 3:** la llave. Token, permisos por vista y el plan que propuso un agente, ejecutado con distintas
   credenciales.
4. **Parte 4:** el duelo. Las mismas pruebas contra una API que escribió una IA, con cuatro fallos.

La guía de laboratorio tiene el paso a paso. Se trabaja **en pareja**, en un solo repositorio.

## Empezar

Un integrante copia este repositorio con **Use this template** y agrega al otro como colaborador.

```powershell
python -m venv myvenv
myvenv\Scripts\activate
pip install -r requirements.txt       # Django y Django REST Framework
python manage.py migrate
python manage.py cargar_datos         # datos FIJOS, más los usuarios admin y agente con su token
python manage.py duelo                # casi todo en rojo: es lo esperado
```

## La API

```text
/api/categorias/              GET lista · POST crea
/api/categorias/<id>/         GET · PUT · PATCH · DELETE
/api/productos/               GET lista (?categoria=<nombre>  ?q=<texto>) · POST crea
/api/productos/<id>/          GET · PUT · PATCH · DELETE
/api/pedidos/                 GET lista (solo con credenciales)
/api/pedidos/<id>/            GET detalle con líneas y total (solo con credenciales)
/api/pedidos/<id>/anular/     POST anula el pedido (solo el personal de la tienda)
/api/token/                   POST usuario y clave → su token
```

Con `python manage.py runserver`, abran http://127.0.0.1:8000/api/productos/ en el navegador: es la **API
navegable** de DRF. Para entrar como un usuario, el enlace «Log in» de arriba a la derecha.

## Usuarios de laboratorio

| Usuario | Clave | Token | Quién es |
|---|---|---|---|
| `admin` | `admin12345` | `admin-token-de-laboratorio-0000000000001` | Personal de la tienda |
| `agente` | `agente12345` | `agente-token-de-laboratorio-00000000002` | La cuenta de un asistente de IA |

Están escritos aquí a propósito, porque es un laboratorio. **En un sistema real, una clave o un token nunca van en
el código ni en el repositorio.**

## Probar desde PowerShell

```powershell
# Leer (sin credenciales)
Invoke-RestMethod http://127.0.0.1:8000/api/productos/?categoria=gaseosas

# Escribir con el token del admin
$h = @{ Authorization = "Token admin-token-de-laboratorio-0000000000001" }
$nuevo = @{ nombre = "Inca Kola 500ml"; categoria = 3; precio = "2.20"; stock = 12 } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/productos/ -Method Post -Headers $h -Body $nuevo -ContentType "application/json"

# Ver el código aunque sea un error: curl.exe (no el alias curl de PowerShell)
curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:8000/api/pedidos/
```

## El plan del agente (Parte 3)

`planes/plan_del_agente.json` es lo que propuso un agente de IA cuando se le pidió «revisa el stock, repón lo que
falte y limpia los pedidos colgados». `ejecutar_plan` lo manda a la API paso a paso, con las credenciales que elijan,
como lo haría el agente sin pantalla:

```powershell
python manage.py ejecutar_plan planes/plan_del_agente.json --como anonimo
python manage.py ejecutar_plan planes/plan_del_agente.json --como agente
python manage.py ejecutar_plan planes/plan_del_agente.json --como admin
```

Es un **simulacro**: al terminar se deshacen los cambios (con `--aplicar` se quedan). La API decide qué pasos se
cumplen; el comando no filtra nada.

## El duelo (Parte 4)

```powershell
python manage.py duelo                      # su versión (tienda/alumno/)
python manage.py duelo ia                   # la API que escribió la IA (tienda/ia/): NO se edita
python manage.py duelo ia --detalle         # por qué falla cada prueba
python manage.py duelo --iniciar-corregida  # copia tienda/ia/ a tienda/corregida/
python manage.py duelo corregida            # su copia corregida: hasta que quede todo en verde
```

Para que `runserver` o `ejecutar_plan` usen otra versión: `$env:TIENDA_VERSION = "ia"` (y vuelvan con
`$env:TIENDA_VERSION = "alumno"`).

**Las pruebas (`tienda/tests/`) no se modifican**: son el oráculo del laboratorio.

## Estructura

```text
extra08/            proyecto Django (settings con DRF y token; urls con todas las rutas)
tienda/models.py    categorías, productos (con costo interno), clientes, pedidos y líneas
tienda/alumno/      SU versión: serializers.py y vistas.py (Partes 1 a 3)
tienda/ia/          la versión de la IA (Parte 4): no se edita
tienda/tests/       las pruebas: no se editan
tienda/management/commands/
    cargar_datos.py     datos fijos y usuarios
    ejecutar_plan.py    ejecuta un plan de llamadas con un token (simulacro)
    duelo.py            corre las pruebas contra una versión y resume por parte
planes/             el plan que propuso el agente
scripts/            su cliente de la API en PowerShell (paso 8)
```
