from django.urls import path
from . import views

urlpatterns = [
    path("calendario/", views.calendario, name="calendario"),
    path("calendario/json/", views.task_feed, name="tareas_json"),
    path("api/tarea/<int:tarea_id>/", views.get_tarea_details, name="tarea_detalles"),
    path("api/tarea/<int:tarea_id>/delete/", views.delete_tarea, name="tarea_delete"),
    path(
        "api/tarea/<int:tarea_id>/toggle/",
        views.toggle_tarea_status,
        name="tarea_toggle",
    ),
]
