from django.urls import path
from . import views

urlpatterns = [
    path('contactos/', views.list_contacts, name='list_contacts'),
    path('contactos/<int:contacto_id>/correos/', views.list_emails, name='list_emails'),
    path('api/contactos/<int:contacto_id>/', views.get_contacto_details, name='get_contacto_details'),
    path('contactos/<int:contacto_id>/correos/get-timeline/', views.get_timeline, name='get_timeline'),
]