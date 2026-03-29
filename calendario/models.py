from django.db import models
from contactos.models import Contacto


# Create your models here.
class Tarea(models.Model):
    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("COMPLETADA", "Completada"),
    ]
    titulo = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=200)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=False)
    fecha_fin = models.DateTimeField()
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="PENDIENTE"
    )

    def __str__(self):
        return (
            f"{self.fecha_inicio} | {self.contacto.empresa.nombre}: {self.descripcion}"
        )
