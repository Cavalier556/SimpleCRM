from django.conf import settings as django_settings
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .tasks import import_sunat_task
from celery.result import AsyncResult
import os
import traceback


# Create your views here.
def settings(request):
    return render(request, "settings.jinja2")


def import_contribuyentes(request):
    if request.method == "POST":
        if not request.FILES.get("file"):
            return JsonResponse({"error": "No file uploaded."}, status=400)

        txt_file = request.FILES["file"]

        # Save file to MEDIA_ROOT/uploads
        location = os.path.join(django_settings.MEDIA_ROOT, "uploads")
        fs = FileSystemStorage(location=location)
        filename = fs.save(txt_file.name, txt_file)
        file_path = fs.path(filename)

        try:
            task = import_sunat_task.delay(file_path)

            # If it's an HTMX request, return a partial for polling
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/import_status.jinja2",
                    {"task_id": task.id, "state": "PENDING"},
                )

            return JsonResponse({"status": "pending", "task_id": task.id})

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
                pass
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse(
        {"error": "Please upload a valid .txt file via POST."}, status=400
    )


def check_task_status(request, task_id):
    res = AsyncResult(task_id)

    if request.headers.get("HX-Request"):
        context = {
            "task_id": task_id,
            "state": res.state,
            "result": res.result if res.ready() else None,
        }
        if res.state == "PROGRESS":
            context["current_count"] = res.info.get("current", 0)

        return render(request, "partials/import_status.jinja2", context)

    response_data = {
        "task_id": task_id,
        "state": res.state,
        "result": res.result if res.ready() else None,
    }
    if res.state == "PROGRESS":
        response_data["current_count"] = res.info.get("current", 0)

    return JsonResponse(response_data)
