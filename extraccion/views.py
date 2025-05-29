from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
import requests
import datetime
import time
import json
import os

from .models import Extraccion, Registro
from .serializers import ExtraccionSerializer, RegistroSerializer

# Create your views here.
def index(request):
    return HttpResponse("Extraccion")

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def crear_extraccion(request):
    """
        Crea un modelo extraccion y le adjunta los registros contenidos
        en un json.
    """
    if request.method == "POST":
        try:
            # leemos contenido json
            data = request.data

            # instancia serializer para validar
            serializer = ExtraccionSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                # si los datos son validos llama al metodo .create()
                # en caso de que un registro sea incorrecto realiza rollback
                with transaction.atomic():

                    extraccion = serializer.save()
                    extraccion.refresh_from_db()

                    return Response({
                        "mensaje": "Extracción creada exitosamente.",
                        "extraccion_id": extraccion.id,
                        "nombre_extraccion": extraccion.nombre
                    }, status=201)
            
            else:
                return Response(serializer.errors, status=400)
        except json.JSONDecodeError:
            return Response({"error": "El cuerpo de la solicitud no es un JSON válido."}, status=400)
        except Exception as e:
            print(f"Error inesperado al crear extracción: {e}")
            return Response({"error": "Ocurrió un error interno del servidor."}, status=500)
    
    else:
        return Response({"error": "Solo se permiten peticiones POST para esta operación."}, status=405)

@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def obtener_extraccion(request, extraccion_id):
    """
        Muestra los registros de una extraccion especifica.
    """

    try:

        # obtenemos valores de fechas
        fecha_inicio = request.form.get("fecha-inicio")
        fecha_fin = request.form.get("fecha-fin")

        # obtenemos las extraccion
        extraccion = get_object_or_404(Extraccion, pk=extraccion_id)
        extraccion.refresh_from_db()

        # obtenemos registros
        registros = extraccion.registro_set.all()

        if fecha_inicio:
            try:
                # Intenta parsear la fecha de inicio (ej. 'YYYY-MM-DD')
                # Si la fecha_creacion es DateTimeField, es mejor usar datetime.datetime
                # Si quieres un rango completo del día, puedes añadir .replace(hour=0, minute=0, second=0, microsecond=0)
                fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
                registros = registros.filter(fecha_creacion__gte=fecha_inicio)
            except ValueError:
                return Response({"error": "Formato de fecha_inicio inválido. Use YYYY-MM-DD."}, status=400)

        if fecha_fin:
            try:
                # Intenta parsear la fecha de fin
                # Para incluir todo el día de fecha_fin, suma un día y usa __lt (less than)
                fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
                fecha_fin_siguiente_dia = fecha_fin + datetime.timedelta(days=1)
                registros = registros.filter(fecha_creacion__lt=fecha_fin_siguiente_dia)
            except ValueError:
                return Response({"error": "Formato de fecha_fin inválido. Use YYYY-MM-DD."}, status=400)

        serializer = RegistroSerializer(registros, many=True)

        # Devuelve los datos serializados en formato JSON
        return Response(serializer.data, status=200)
    
    except Extraccion.DoesNotExist:
        return Response({"detail": "Extracción no encontrada."}, status=404)
    except Exception as e:
        print(f"Error inesperado al obtener registros: {e}")
        return Response({"error": "Ocurrió un error interno del servidor al intentar obtener los registros."}, status=500)
    

def mostrar_extracciones(request):
    """
        Muestra todas las extracciones creadas
    """
    
    extracciones = Extraccion.objects.all()
    mensajes = []

    if request.method == "POST":

        # obtenemos informacion de form
        nombreExtraccion = request.POST.get("nombreExtraccion")
        btnCrear = request.POST.get("btnCrear")

        id_extraccion = request.POST.get("id_extraccion")
        btnBorrar = request.POST.get("btnBorrar")
        btnSeleccionar = request.POST.get("btnSeleccionar")

        if btnCrear == "Crear" and nombreExtraccion:

            # espera un poco, un poquito mas
            time.sleep(15)

            json_file_path = None

            for static_dir in settings.STATICFILES_DIRS:
                potential_path = os.path.join(static_dir, 'data', 'example.json')
                if os.path.exists(potential_path):
                    json_file_path = potential_path
                    break
            
            # Si el JSON estuviera en una subcarpeta de 'static', por ejemplo 'static/config/data.json'
            # deberías ajustar la ruta interna: os.path.join(static_dir, 'config', 'data.json')

            if json_file_path:
                try:
                    # Leer el contenido del archivo JSON
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        extraccion_json = json.load(f)

                    extraccion_json["nombre"] = nombreExtraccion

                    # obtenemos las cookies de sesion
                    csrf_token = get_token(request)
                    id_session = request.session.session_key

                    str_cookie = f"csrftoken={csrf_token}; sessionid={id_session}"

                    cabecera = {
                        "Accept": "*/*",
                        "Content-Type": "application/json",
                        "Cookie": str_cookie,
                        "X-CSRFToken": csrf_token
                    }

                    # obtenemos la url del endpoint crear extraccion
                    url_relativa = reverse('extraccion:crear_extraccion')
                    url_absoluta = request.build_absolute_uri(url_relativa)

                    respuesta = requests.post(url=url_absoluta, headers=cabecera, json=extraccion_json)

                    if respuesta.status_code in [200, 201]:
                        mensajes.append(f"Extraccion creada con éxito. Respuesta: {respuesta.json()}")
                    else:
                        mensajes.append(f"Error al crear extraccion. Código: {respuesta.status_code}, Error: {respuesta.text}")

                except json.JSONDecodeError:
                    return render(request, 'error.html', {'mensaje': "Error al decodificar el archivo JSON. Asegúrate de que el formato sea válido.", 'error': 400})
                except requests.exceptions.RequestException as e:
                    return render(request, 'error.html', {'mensaje': f"Error al conectar con la API: {e}", 'error': 500})
                
        elif btnSeleccionar:
            # obtenemos la extraccion
            seleccionar_extraccion = Extraccion.objects.get(pk=id_extraccion)
            # guardamos el id de la extraccion en la sesion
            request.session["id_extraccion"] = id_extraccion
            return HttpResponseRedirect(reverse('dashboard:tabla_registros'))
        elif btnBorrar:
            # obtenemos la extraccion
            borrar_extraccion = Extraccion.objects.get(pk=id_extraccion)
            # borramos la extraccion
            borrar_extraccion.delete()
        

    contexto = {
        "extracciones": extracciones,
    }

    return render(request, "extraccion/extracciones.html", contexto)