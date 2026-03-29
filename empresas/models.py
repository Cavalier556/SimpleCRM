from django.db import models
from django.core.validators import MinLengthValidator

# Create your models here.
class Empresa(models.Model):
    ruc = models.CharField(max_length=11, validators=[MinLengthValidator(4)], unique=True)
    nombre = models.CharField(max_length=50)
    rubro = models.CharField(max_length=30)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=11)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.ruc} | {self.nombre}'

class Contribuyente(models.Model):
    ruc = models.CharField(max_length=11)
    nombre_razon_social = models.CharField(max_length=255)
    direccion = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.ruc} - {self.nombre_razon_social}"