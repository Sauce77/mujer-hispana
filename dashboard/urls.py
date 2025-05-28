from django.urls import path
from . import views

app_name = 'dashboard' 

urlpatterns = [
    path('', views.mostrar_dashboard, name='mostrar_dashboard'),
    path('tabla/', views.tabla_registros, name='tabla_registros'),
]