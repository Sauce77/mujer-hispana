from django.shortcuts import render, get_object_or_404, HttpResponse
from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
import datetime
import json

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
    
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def mostrar_extracciones(request):
    """
        Muestra todas las extracciones creadas
    """
    
    extracciones = Extraccion.objects.all()

    serializer = ExtraccionSerializer(extracciones, many=True)

    return Response(serializer.data, status=200)
