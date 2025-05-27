from django.shortcuts import render
from django.http import JsonResponse
from django.db import IntegrityError, transaction
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
import json

from .models import Extraccion, Registro
from .serializers import ExtraccionSerializer


# Create your views here.
def index():
    return "Extraccion"

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
            data = json.loads(request.body)

            # instancia serializer para validar
            serializer = ExtraccionSerializer(data=data)

            if serializer.is_valid():
                # si los datos son validos llama al metodo .create()
                # en caso de que un registro sea incorrecto realiza rollback
                with transaction.atomic():

                    extraccion = serializer.save()

                    return JsonResponse({
                        "mensaje": "Extracción creada exitosamente.",
                        "extraccion_id": extraccion.id,
                        "nombre_extraccion": extraccion.nombre,
                        "cantidad_registros": extraccion.registros.count()
                    }, status=201)
            
            else:
                return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "El cuerpo de la solicitud no es un JSON válido."}, status=400)
        except Exception as e:
            print(f"Error inesperado al crear extracción: {e}")
            return JsonResponse({"error": "Ocurrió un error interno del servidor."}, status=500)
    
    else:
        return JsonResponse({"error": "Solo se permiten peticiones POST para esta operación."}, status=405)

            

