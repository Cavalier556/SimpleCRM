from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/empresa/<int:empresa_id>/', views.get_empresa_details, name='get_empresa_details'),
    path('api/sunat/<int:ruc>/', views.get_sunat_data, name='get_sunat_data'),
    
]