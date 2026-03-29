from django.shortcuts import render, redirect
from .models import Empresa, Contribuyente
from calendario.models import Tarea
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import connection
import io

from django.http import JsonResponse


# Create your views here.
def home(request):
    if request.method == 'POST':
        ruc = request.POST.get('ruc')
        nombre = request.POST.get('nombre')
        rubro = request.POST.get('rubro')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')

        Empresa.objects.create(ruc=ruc,nombre=nombre,rubro=rubro,direccion=direccion,telefono=telefono)

        return redirect('home')

    query = request.GET.get("nombre")
    if query:
        empresas = Empresa.objects.filter(nombre__icontains=query)
    else:
        empresas = Empresa.objects.order_by('nombre').all()
    pendientes = Tarea.objects.filter(estado="PENDIENTE").all()
    return render(request,'index.jinja2', {'empresas': empresas, 'pendientes': pendientes})



def get_empresa_details(request, empresa_id):
    empresa = get_object_or_404(Empresa, id=empresa_id)

    if request.method == "POST":
        empresa.ruc = request.POST.get("ruc")
        empresa.nombre = request.POST.get("nombre")
        empresa.rubro = request.POST.get("rubro")
        empresa.direccion = request.POST.get("direccion")
        empresa.telefono = request.POST.get("telefono")

        empresa.save()
        return JsonResponse({"msg": "Completado"}, headers={'HX-Refresh': 'true'})

    return render(request,'partials/empresa_detalles.jinja2', {'empresa': empresa})

def get_sunat_data(request, ruc):
    contribuyente = get_object_or_404(Contribuyente, ruc=ruc)
    data = {
        "nombre": contribuyente.nombre_razon_social,
        "direccion": contribuyente.direccion,
    }
    return JsonResponse(data)

