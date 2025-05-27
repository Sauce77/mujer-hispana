from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Extraccion, Registro

User = get_user_model() # obtiene la sesion actual

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        exclude = ["extraccion", ]

class ExtraccionSerializer(serializers.ModelSerializer):
    registros = RegistroSerializer(many=True, required=False) # 'required=False' si una extracción puede crearse inicialmente sin registros

    class Meta:
        model = Extraccion
        fields = "__all__"
        read_only_fields = ['id', 'fecha_creacion', 'usuario']

    def create(self, validated_data):
        # Separar los datos de registros de los datos de la extracción
        registros_data = validated_data.pop('registros', [])

         # --- Manejo del campo 'user' ---
        # Accede al usuario de la request a través del contexto del serializer.
        # El contexto se pasa desde la vista.
        user = self.context.get('request').user if self.context.get('request') else None

        if not user or not user.is_authenticated:
            # Esto nunca debería ocurrir si tus permisos son correctos,
            # pero es una buena salvaguarda.
            raise serializers.ValidationError("Usuario no autenticado para crear una extracción.")

        # Asigna el usuario validado a los validated_data antes de crear la Extraccion
        validated_data['usuario'] = user
        # --- Fin del manejo del campo 'user' ---

        # Crear la instancia de Extraccion
        extraccion = Extraccion.objects.create(**validated_data)

        # Crear los Registros asociados a la Extraccion
        registros_a_crear = []
        for registro_data in registros_data:
            registros_a_crear.append(
                Registro(extraccion=extraccion, **registro_data)
            )
        Registro.objects.bulk_create(registros_a_crear)

        return extraccion