from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Extraccion(models.Model):
    """
        Representa una extraccion creada por usuario.
    """
    nombre = models.CharField(max_length=100, null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False, blank=False)

    def __str__(self):
        return self.nombre
    

class Registro(models.Model):
    """
        Representa un dato tomado de la extraccion.
    """
    num_nota = models.CharField(max_length=200, null=True, blank=True)
    folio = models.CharField(max_length=200, null=True, blank=True)
    tienda = models.CharField(max_length=100, null=True, blank=True)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    abonado = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    debe = total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    tipo = models.CharField(max_length=100)
    extraccion = models.ForeignKey(Extraccion, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.num_nota