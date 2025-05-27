from rest_framework import serializers
from .models import Extraccion, Registro

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = "__all__"

class ExtraccionSerializer(serializers.ModelSerializer):
    egistros = RegistroSerializer(many=True, required=False) # 'required=False' si una extracción puede crearse inicialmente sin registros

    class Meta:
        model = Extraccion
        fields = ['id', 'nombre', 'registros'] # Incluye 'registros' para que el serializer lo procese
        read_only_fields = ['id'] # El ID se genera al crear la extracción

    def create(self, validated_data):
        # Separar los datos de registros de los datos de la extracción
        registros_data = validated_data.pop('registros', [])

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