from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Tarea
from contactos.models import Contacto


# Create your views here.
def calendario(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        contacto_id = request.POST.get("contacto")

        contacto = get_object_or_404(Contacto, id=contacto_id)

        Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            contacto=contacto,
        )
        return redirect("calendario")

    contactos = Contacto.objects.all()
    return render(request, "calendario.jinja2", {"contactos": contactos})


def task_feed(request):
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    tareas = Tarea.objects.all()

    if start_date and end_date:
        tareas = tareas.filter(fecha_inicio__gte=start_date, fecha_fin__lte=end_date)

    event_list = []
    for tarea in tareas:
        color = "#758bfd" if tarea.estado == "PENDIENTE" else "#10b981"
        event_list.append(
            {
                "id": tarea.id,
                "title": f"{tarea.titulo} | {tarea.contacto.empresa.nombre}",
                "start": tarea.fecha_inicio.isoformat(),
                "end": tarea.fecha_fin.isoformat() if tarea.fecha_fin else None,
                "backgroundColor": color,
                "borderColor": color,
                "extendedProps": {
                    "description": tarea.descripcion,
                    "contacto": f"{tarea.contacto.nombre} {tarea.contacto.apellido}",
                    "estado": tarea.get_estado_display(),
                },
            }
        )
    return JsonResponse(event_list, safe=False)


def get_tarea_details(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    contactos = Contacto.objects.all()

    if request.method == "POST":
        tarea.titulo = request.POST.get("titulo")
        tarea.descripcion = request.POST.get("descripcion")
        tarea.fecha_inicio = request.POST.get("fecha_inicio")
        tarea.fecha_fin = request.POST.get("fecha_fin")
        tarea.estado = request.POST.get("estado", tarea.estado)
        contacto_id = request.POST.get("contacto")
        tarea.contacto = get_object_or_404(Contacto, id=contacto_id)
        tarea.save()
        return JsonResponse({"msg": "Completado"}, headers={'HX-Refresh': 'true'})

    return render(
        request,
        "partials/tarea_detalles.jinja2",
        {"tarea": tarea, "contactos": contactos},
    )


def delete_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == "POST":
        tarea.delete()
        return redirect("calendario")
    return JsonResponse({"error": "Method not allowed"}, status=405)


def toggle_tarea_status(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == "POST":
        if tarea.estado == "PENDIENTE":
            tarea.estado = "COMPLETADA"
        else:
            tarea.estado = "PENDIENTE"
        tarea.save()
        return JsonResponse({"msg": "Completado"}, headers={'HX-Refresh': 'true'})
    return JsonResponse({"error": "Method not allowed"}, status=405)
