from django.urls import path
from . import views

urlpatterns = [
    path("configuracion/", views.settings, name="configuracion"),
    path(
        "configuracion/sunat/",
        views.import_contribuyentes,
        name="import_contribuyentes",
    ),
    path(
        "configuracion/task-status/<str:task_id>/",
        views.check_task_status,
        name="check_task_status",
    ),
]
