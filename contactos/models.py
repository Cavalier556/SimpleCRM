from django.db import models
from empresas.models import Empresa

# Create your models here.
class Contacto(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    correo = models.EmailField(max_length=30)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=25)
    telefono = models.CharField(max_length=11)
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'