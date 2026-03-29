from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Contacto
from import_email import getEmailsForAddress
from django.shortcuts import get_object_or_404
from django.db.models import Q
from empresas.models import Empresa

# Create your views here.
def list_contacts(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        empresa_id = request.POST.get('empresa')
        empresa = Empresa.objects.get(pk=empresa_id)
        cargo = request.POST.get('cargo')
        telefono = request.POST.get('telefono')

        Contacto.objects.create(nombre=nombre,apellido=apellido,correo=correo,empresa=empresa,cargo=cargo,telefono=telefono)

        return redirect('list_contacts')

    query = request.GET.get("nombre")

    if query:
        contactos = Contacto.objects.filter(Q(nombre__icontains=query) | Q(empresa__nombre__icontains=query))
    else:
        contactos = Contacto.objects.order_by('empresa').all()

    empresas = Empresa.objects.order_by('nombre').all()
    context = {"contactos": contactos, "empresas": empresas}
    return render(request, "list_contacts.jinja2", context)


def list_emails(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    return render(
        request, "list_emails.jinja2", {"contacto": contacto}
    )

def get_contacto_details(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)

    if request.method == "POST":
        contacto.ruc = request.POST.get("ruc")
        contacto.nombre = request.POST.get("nombre")
        contacto.rubro = request.POST.get("rubro")
        contacto.direccion = request.POST.get("direccion")
        contacto.telefono = request.POST.get("telefono")

        contacto.save()
        return JsonResponse({"msg": "Completado"}, headers={'HX-Refresh': 'true'})

    empresas = Empresa.objects.order_by('nombre').all()
    return render(request,'partials/contacto_detalles.jinja2', {'contacto':contacto,'empresas': empresas})

def get_timeline(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    emails = getEmailsForAddress(contacto.correo)
    return render(
        request, "partials/timeline.jinja2", {"emails": emails, "contacto": contacto}
    )